# -*- coding: utf-8 -*-
"""Daily IntroDB open-data mirror with a local SQLite lookup index.

The source CSVs are downloaded only when the daily manifest changes. A verified
local database remains available when the network is offline.
"""
import csv
import gzip
import hashlib
import io
import json
import os
import re
import sqlite3
import threading

import requests
import xbmcvfs

from resources.lib import settings, tools


class IntroDBOpenDataAdapter:
    BASE_URL = "https://data.introdb.app/latest/"
    MANIFEST_URL = BASE_URL + "manifest.json"
    FILE_NAMES = ("segments.csv.gz", "segmentless.csv.gz")
    IMDB_PATTERN = re.compile(r"^tt[0-9]{7,10}$", re.I)

    def __init__(self, profile_path=None, timeout=15):
        if profile_path is None:
            profile_path = xbmcvfs.translatePath(settings.get_addon_info("profile"))
        self.data_dir = os.path.join(str(profile_path), "introdb-open-data")
        self.db_path = os.path.join(self.data_dir, "introdb.sqlite")
        self.manifest_path = os.path.join(self.data_dir, "manifest.json")
        self.timeout = timeout
        self._sync_lock = threading.Lock()
        self._sync_thread = None

    def start_background_sync(self):
        """Check the daily manifest without delaying Kodi startup or playback."""
        if self._sync_thread is not None and self._sync_thread.is_alive():
            return self._sync_thread
        self._sync_thread = threading.Thread(
            target=self.sync_if_needed,
            name="IntroSkip-IntroDB-OpenData",
            daemon=True,
        )
        self._sync_thread.start()
        return self._sync_thread

    @property
    def is_ready(self):
        return os.path.isfile(self.db_path)

    def sync_if_needed(self):
        """Download and atomically replace the local index only when changed."""
        if not self._sync_lock.acquire(False):
            return False
        temp_db = self.db_path + ".tmp"
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            response = requests.get(self.MANIFEST_URL, timeout=self.timeout)
            response.raise_for_status()
            manifest_bytes = response.content
            manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
            if not isinstance(manifest, dict):
                raise ValueError("IntroDB manifest is not a JSON object")
            remote_hash = hashlib.sha256(manifest_bytes).hexdigest()

            if self.is_ready and os.path.isfile(self.manifest_path):
                try:
                    with open(self.manifest_path, "rb") as handle:
                        current_hash = hashlib.sha256(handle.read()).hexdigest()
                    if current_hash == remote_hash:
                        tools.log("IntroDB open-data snapshot is already current", "debug")
                        return False
                except OSError:
                    pass

            payloads = {}
            for filename in self.FILE_NAMES:
                info = self._file_metadata(manifest, filename)
                url = self.BASE_URL + filename
                file_response = requests.get(url, timeout=self.timeout)
                file_response.raise_for_status()
                payload = file_response.content
                expected_sha = self._metadata_value(info, ("sha256", "sha_256", "checksum"))
                if expected_sha:
                    expected_sha = str(expected_sha).lower().replace("sha256:", "").strip()
                    actual_sha = hashlib.sha256(payload).hexdigest()
                    if actual_sha != expected_sha:
                        raise ValueError("{} failed SHA-256 verification".format(filename))
                expected_size = self._metadata_value(
                    info, ("compressed_size", "size_bytes", "bytes", "size")
                )
                if expected_size is not None:
                    try:
                        expected_size = int(expected_size)
                    except (TypeError, ValueError):
                        expected_size = 0
                    if expected_size > 0 and expected_size != len(payload):
                        tools.log(
                            "{} size differs from manifest ({} vs {}); SHA-256 remains authoritative".format(
                                filename, len(payload), expected_size
                            ),
                            "warning",
                        )
                # Reading to EOF verifies the gzip trailer/CRC before the old
                # database can be replaced.
                with gzip.GzipFile(fileobj=io.BytesIO(payload), mode="rb") as stream:
                    while stream.read(1024 * 256):
                        pass
                payloads[filename] = payload

            if os.path.exists(temp_db):
                os.remove(temp_db)
            self._build_database(temp_db, payloads)
            os.replace(temp_db, self.db_path)
            manifest_tmp = self.manifest_path + ".tmp"
            with open(manifest_tmp, "wb") as handle:
                handle.write(manifest_bytes)
            os.replace(manifest_tmp, self.manifest_path)
            tools.log(
                "IntroDB open-data index updated successfully ({})".format(
                    manifest.get("generated_at") or manifest.get("exported_at") or "new snapshot"
                ),
                "info",
            )
            return True
        except (requests.exceptions.RequestException, ValueError, OSError, sqlite3.Error, EOFError) as exc:
            tools.log("IntroDB open-data sync failed; retaining previous local data: {}".format(exc), "warning")
            try:
                if os.path.exists(temp_db):
                    os.remove(temp_db)
            except OSError:
                pass
            return False
        finally:
            self._sync_lock.release()

    @staticmethod
    def _metadata_value(info, names):
        if not isinstance(info, dict):
            return None
        for name in names:
            if info.get(name) is not None:
                return info.get(name)
        return None

    @classmethod
    def _file_metadata(cls, manifest, filename):
        """Accept the documented keyed or list-style file metadata layouts."""
        def walk(value):
            if isinstance(value, dict):
                direct = value.get(filename)
                if isinstance(direct, dict):
                    return direct
                if value.get("name") == filename or value.get("file") == filename:
                    return value
                for child in value.values():
                    found = walk(child)
                    if found is not None:
                        return found
            elif isinstance(value, list):
                for child in value:
                    found = walk(child)
                    if found is not None:
                        return found
            return None
        return walk(manifest) or {}

    @staticmethod
    def _integer(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError, OverflowError):
            return default

    @staticmethod
    def _boolean(value):
        return str(value or "").strip().lower() in ("1", "t", "true", "yes", "y")

    @staticmethod
    def _segment(value):
        value = str(value or "").strip().lower().replace("-", "_")
        return "post_credits" if value in ("post_credits", "postcredits") else value

    def _build_database(self, path, payloads):
        connection = sqlite3.connect(path)
        try:
            connection.execute("PRAGMA journal_mode=DELETE")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("""
                CREATE TABLE segments (
                    id INTEGER PRIMARY KEY,
                    imdb_id TEXT NOT NULL,
                    is_movie INTEGER NOT NULL,
                    season INTEGER NOT NULL,
                    episode INTEGER NOT NULL,
                    segment TEXT NOT NULL,
                    start_ms INTEGER NOT NULL,
                    end_ms INTEGER NOT NULL,
                    confidence REAL,
                    submission_count INTEGER,
                    updated_at TEXT
                )
            """)
            connection.execute("""
                CREATE INDEX idx_segments_lookup
                ON segments(imdb_id, is_movie, season, episode, segment)
            """)
            connection.execute("""
                CREATE TABLE segmentless (
                    imdb_id TEXT NOT NULL,
                    is_movie INTEGER NOT NULL,
                    season INTEGER NOT NULL,
                    episode INTEGER NOT NULL,
                    segment TEXT NOT NULL,
                    updated_at TEXT,
                    UNIQUE(imdb_id, is_movie, season, episode, segment)
                )
            """)
            with gzip.GzipFile(fileobj=io.BytesIO(payloads["segments.csv.gz"]), mode="rb") as zipped:
                with io.TextIOWrapper(zipped, encoding="utf-8-sig", newline="") as source:
                    reader = csv.DictReader(source)
                    required = {"imdb_id", "is_movie", "season", "episode", "segment", "start_ms", "end_ms"}
                    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                        raise ValueError("segments.csv.gz is missing required columns")
                    batch = []
                    for row in reader:
                        imdb_id = str(row.get("imdb_id") or "").strip().lower()
                        segment = self._segment(row.get("segment"))
                        start_ms = self._integer(row.get("start_ms"), -1)
                        end_ms = self._integer(row.get("end_ms"), -1)
                        if (not self.IMDB_PATTERN.match(imdb_id) or not segment
                                or start_ms < 0 or end_ms <= start_ms):
                            continue
                        try:
                            confidence = float(row.get("confidence")) if row.get("confidence") not in (None, "") else None
                        except (TypeError, ValueError, OverflowError):
                            confidence = None
                        batch.append((
                            imdb_id, int(self._boolean(row.get("is_movie"))),
                            self._integer(row.get("season")), self._integer(row.get("episode")),
                            segment, start_ms, end_ms, confidence,
                            self._integer(row.get("submission_count"), 0),
                            str(row.get("updated_at") or ""),
                        ))
                        if len(batch) >= 2000:
                            connection.executemany("""
                                INSERT INTO segments
                                (imdb_id,is_movie,season,episode,segment,start_ms,end_ms,
                                 confidence,submission_count,updated_at)
                                VALUES (?,?,?,?,?,?,?,?,?,?)
                            """, batch)
                            batch = []
                    if batch:
                        connection.executemany("""
                            INSERT INTO segments
                            (imdb_id,is_movie,season,episode,segment,start_ms,end_ms,
                             confidence,submission_count,updated_at)
                            VALUES (?,?,?,?,?,?,?,?,?,?)
                        """, batch)

            with gzip.GzipFile(fileobj=io.BytesIO(payloads["segmentless.csv.gz"]), mode="rb") as zipped:
                with io.TextIOWrapper(zipped, encoding="utf-8-sig", newline="") as source:
                    reader = csv.DictReader(source)
                    required = {"imdb_id", "is_movie", "season", "episode", "segment"}
                    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                        raise ValueError("segmentless.csv.gz is missing required columns")
                    batch = []
                    for row in reader:
                        imdb_id = str(row.get("imdb_id") or "").strip().lower()
                        segment = self._segment(row.get("segment"))
                        if not self.IMDB_PATTERN.match(imdb_id) or segment not in ("intro", "recap", "outro"):
                            continue
                        batch.append((
                            imdb_id, int(self._boolean(row.get("is_movie"))),
                            self._integer(row.get("season")), self._integer(row.get("episode")),
                            segment, str(row.get("updated_at") or ""),
                        ))
                    if batch:
                        connection.executemany("""
                            INSERT OR REPLACE INTO segmentless
                            (imdb_id,is_movie,season,episode,segment,updated_at)
                            VALUES (?,?,?,?,?,?)
                        """, batch)
            connection.commit()
            count = connection.execute("SELECT COUNT(*) FROM segments").fetchone()[0]
            if count < 1:
                raise ValueError("IntroDB snapshot contains no usable segment rows")
            tools.log("Built local IntroDB index with {} live segment rows".format(count), "info")
        finally:
            connection.close()

    def get_episode_data(self, imdb, season=0, episode=0, is_movie=False):
        """Return API-shaped data from the local index, or None if not indexed."""
        imdb_id = str(imdb or "").strip().lower()
        if not self.IMDB_PATTERN.match(imdb_id) or not self.is_ready:
            return None
        is_movie = bool(is_movie)
        try:
            season = 0 if is_movie else int(season)
            episode = 0 if is_movie else int(episode)
        except (TypeError, ValueError, OverflowError):
            return None
        try:
            connection = sqlite3.connect(self.db_path, timeout=2)
            connection.row_factory = sqlite3.Row
            try:
                rows = connection.execute("""
                    SELECT segment,start_ms,end_ms,confidence,submission_count,updated_at
                    FROM segments
                    WHERE imdb_id=? AND is_movie=? AND season=? AND episode=?
                    ORDER BY segment,start_ms
                """, (imdb_id, int(is_movie), season, episode)).fetchall()
                absent = connection.execute("""
                    SELECT segment FROM segmentless
                    WHERE imdb_id=? AND is_movie=? AND season=? AND episode=?
                """, (imdb_id, int(is_movie), season, episode)).fetchall()
            finally:
                connection.close()
        except sqlite3.Error as exc:
            tools.log("Local IntroDB lookup failed: {}".format(exc), "warning")
            return None
        if not rows and not absent:
            return None
        data = {
            "imdb_id": imdb_id,
            "media_type": "movie" if is_movie else "tv",
            "is_movie": is_movie,
            "season": season,
            "episode": episode,
            "intro": [],
            "recap": [],
            "outro": [],
            "post_credits": [],
            "no_intro": False,
            "no_recap": False,
            "no_outro": False,
        }
        for row in rows:
            segment = self._segment(row["segment"])
            if segment not in ("intro", "recap", "outro", "post_credits"):
                continue
            data[segment].append({
                "start_ms": row["start_ms"],
                "end_ms": row["end_ms"],
                "confidence": row["confidence"],
                "submission_count": row["submission_count"],
                "updated_at": row["updated_at"],
            })
        for row in absent:
            data["no_{}".format(row["segment"])] = True
        for segment in ("intro", "recap", "outro", "post_credits"):
            if len(data[segment]) == 1:
                data[segment] = data[segment][0]
            elif not data[segment]:
                data[segment] = None
        return data
