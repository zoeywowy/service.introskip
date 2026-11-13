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
import math
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
        self._db_validation_lock = threading.Lock()
        self._db_validated = False
        self._db_is_valid = False

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
        """Return whether the local index exists and passes a lightweight integrity check."""
        return self._database_is_valid()

    def _database_is_valid(self, force=False):
        """Validate the SQLite file once per adapter instance; never trust a corrupt cache."""
        with self._db_validation_lock:
            if self._db_validated and not force:
                return self._db_is_valid

            valid = False
            if os.path.isfile(self.db_path):
                connection = None
                try:
                    connection = sqlite3.connect(self.db_path, timeout=2)
                    check = connection.execute("PRAGMA quick_check(1)").fetchone()
                    tables = {
                        row[0] for row in connection.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        ).fetchall()
                    }
                    valid = bool(
                        check and check[0] == "ok"
                        and {"segments", "segmentless"}.issubset(tables)
                    )
                except sqlite3.Error:
                    valid = False
                finally:
                    if connection is not None:
                        connection.close()

            self._db_is_valid = valid
            self._db_validated = True
            return valid

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
                expected_sha = str(expected_sha or "").lower().replace("sha256:", "").strip()
                if not re.fullmatch(r"[0-9a-f]{64}", expected_sha):
                    raise ValueError("Manifest is missing a valid SHA-256 for {}".format(filename))
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
            with self._db_validation_lock:
                self._db_validated = False
                self._db_is_valid = False
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
        value = str(value or "").strip().lower()
        if value in ("1", "t", "true", "yes", "y"):
            return True
        if value in ("0", "f", "false", "no", "n"):
            return False
        return None

    @staticmethod
    def _segment(value):
        value = str(value or "").strip().lower().replace("-", "_")
        return "post_credits" if value in ("post_credits", "postcredits") else value

    def _build_database(self, path, payloads):
        """Build a complete, validated SQLite index from the two documented CSV exports."""
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
                    required = {
                        "imdb_id", "is_movie", "season", "episode",
                        "segment", "start_ms", "end_ms",
                    }
                    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                        raise ValueError("segments.csv.gz is missing required columns")

                    batch = []
                    rows_seen = 0
                    rows_accepted = 0
                    for row in reader:
                        rows_seen += 1
                        imdb_id = str(row.get("imdb_id") or "").strip().lower()
                        is_movie = self._boolean(row.get("is_movie"))
                        season = self._integer(row.get("season"), -1)
                        episode = self._integer(row.get("episode"), -1)
                        segment = self._segment(row.get("segment"))
                        start_ms = self._integer(row.get("start_ms"), -1)
                        end_ms = self._integer(row.get("end_ms"), -1)

                        if (
                            not self.IMDB_PATTERN.fullmatch(imdb_id)
                            or is_movie is None
                            or season < 0
                            or episode < 0
                            or (is_movie and (season != 0 or episode != 0))
                            or segment not in ("intro", "recap", "outro", "post_credits")
                            or start_ms < 0
                            or end_ms <= start_ms
                            or end_ms >= 86400000
                        ):
                            continue

                        try:
                            confidence = (
                                float(row.get("confidence"))
                                if row.get("confidence") not in (None, "") else None
                            )
                            if confidence is not None and (
                                not math.isfinite(confidence) or not 0 <= confidence <= 1
                            ):
                                confidence = None
                        except (TypeError, ValueError, OverflowError):
                            confidence = None

                        submissions = max(0, self._integer(row.get("submission_count"), 0))
                        batch.append((
                            imdb_id, int(is_movie), season, episode, segment,
                            start_ms, end_ms, confidence, submissions,
                            str(row.get("updated_at") or ""),
                        ))
                        rows_accepted += 1

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
                    if rows_seen and not rows_accepted:
                        raise ValueError("segments.csv.gz contains no usable timestamp rows")

            with gzip.GzipFile(fileobj=io.BytesIO(payloads["segmentless.csv.gz"]), mode="rb") as zipped:
                with io.TextIOWrapper(zipped, encoding="utf-8-sig", newline="") as source:
                    reader = csv.DictReader(source)
                    required = {"imdb_id", "is_movie", "season", "episode", "segment"}
                    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                        raise ValueError("segmentless.csv.gz is missing required columns")

                    batch = []
                    rows_seen = 0
                    rows_accepted = 0
                    for row in reader:
                        rows_seen += 1
                        imdb_id = str(row.get("imdb_id") or "").strip().lower()
                        is_movie = self._boolean(row.get("is_movie"))
                        season = self._integer(row.get("season"), -1)
                        episode = self._integer(row.get("episode"), -1)
                        segment = self._segment(row.get("segment"))

                        if (
                            not self.IMDB_PATTERN.fullmatch(imdb_id)
                            or is_movie is None
                            or season < 0
                            or episode < 0
                            or (is_movie and (season != 0 or episode != 0))
                            or segment not in ("intro", "recap", "outro")
                        ):
                            continue

                        batch.append((
                            imdb_id, int(is_movie), season, episode,
                            segment, str(row.get("updated_at") or ""),
                        ))
                        rows_accepted += 1

                    if batch:
                        connection.executemany("""
                            INSERT OR REPLACE INTO segmentless
                            (imdb_id,is_movie,season,episode,segment,updated_at)
                            VALUES (?,?,?,?,?,?)
                        """, batch)
                    if rows_seen and not rows_accepted:
                        raise ValueError("segmentless.csv.gz contains no usable confirmation rows")

            # Build the lookup index after bulk insertion for a faster first sync.
            connection.execute("""
                CREATE INDEX idx_segments_lookup
                ON segments(imdb_id, is_movie, season, episode, segment)
            """)
            connection.commit()

            segment_count = connection.execute("SELECT COUNT(*) FROM segments").fetchone()[0]
            segmentless_count = connection.execute("SELECT COUNT(*) FROM segmentless").fetchone()[0]
            if segment_count + segmentless_count < 1:
                raise ValueError("IntroDB snapshot contains no usable rows")

            integrity = connection.execute("PRAGMA quick_check(1)").fetchone()
            if not integrity or integrity[0] != "ok":
                raise ValueError("IntroDB SQLite index failed its integrity check")

            tools.log(
                "Built local IntroDB index with {} timestamp rows and {} confirmed-absent rows".format(
                    segment_count, segmentless_count
                ),
                "info",
            )
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
