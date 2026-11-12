# -*- coding: utf-8 -*-
"""TheIntroDB v4 adapter with duration-aware matching and a small local response cache."""
import hashlib
import json
import os
import time

import requests
import xbmcvfs

from resources.lib import settings, tools


class TheIntroDBAdapter:
    BASE_URL = "https://api.theintrodb.org/v4/media"
    CACHE_TTL = 7 * 24 * 60 * 60

    def __init__(self, profile_path=None, timeout=5):
        if profile_path is None:
            profile_path = xbmcvfs.translatePath(settings.get_addon_info("profile"))
        self.cache_dir = os.path.join(str(profile_path), "theintrodb-cache")
        self.timeout = timeout

    @staticmethod
    def _valid_imdb(value):
        value = str(value or "").strip().lower()
        return value if value.startswith("tt") and value[2:].isdigit() else None

    def _cache_path(self, key):
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, digest + ".json")

    def _read_cache(self, path, allow_stale=False):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                entry = json.load(handle)
            age = time.time() - float(entry.get("fetched_at", 0))
            if isinstance(entry.get("payload"), dict) and (allow_stale or age <= self.CACHE_TTL):
                return entry["payload"]
        except (OSError, ValueError, TypeError):
            pass
        return None

    def get_media_data(self, imdb, season=0, episode=0, is_movie=False, duration_ms=0):
        """Fetch one title/episode; reads are anonymous, IMDb is a supported fallback ID."""
        imdb_id = self._valid_imdb(imdb)
        if not imdb_id:
            return None
        try:
            duration_ms = int(duration_ms or 0)
        except (TypeError, ValueError, OverflowError):
            duration_ms = 0
        duration_ms = duration_ms if duration_ms > 0 else 0
        if is_movie:
            key = "{}|movie|{}".format(imdb_id, duration_ms)
        else:
            try:
                season, episode = int(season), int(episode)
            except (TypeError, ValueError, OverflowError):
                return None
            if season < 0 or episode < 0:
                return None
            key = "{}|tv|{}|{}|{}".format(imdb_id, season, episode, duration_ms)
        cache_path = self._cache_path(key)
        cached = self._read_cache(cache_path)
        if cached is not None:
            tools.log("TheIntroDB cache hit for {}".format(key), "debug")
            return None if cached.get("_no_data") else cached

        params = {"imdb_id": imdb_id, "details": "true"}
        if not is_movie:
            params.update({"season": season, "episode": episode})
        if duration_ms:
            params["duration_ms"] = duration_ms
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
            if response.status_code == 404:
                os.makedirs(self.cache_dir, exist_ok=True)
                temp_path = cache_path + ".tmp"
                with open(temp_path, "w", encoding="utf-8") as handle:
                    json.dump({"fetched_at": time.time(), "payload": {"_no_data": True}}, handle)
                os.replace(temp_path, cache_path)
                tools.log("TheIntroDB has no published data for {}".format(key), "debug")
                return None
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                return None
            os.makedirs(self.cache_dir, exist_ok=True)
            temp_path = cache_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as handle:
                json.dump({"fetched_at": time.time(), "payload": data}, handle, separators=(",", ":"))
            os.replace(temp_path, cache_path)
            tools.log("TheIntroDB v4 returned data for {}".format(key), "info")
            return data
        except requests.exceptions.RequestException as exc:
            tools.log("TheIntroDB v4 request failed: {}".format(exc), "warning")
            stale = self._read_cache(cache_path, allow_stale=True)
            return stale
        except (ValueError, TypeError, OSError) as exc:
            tools.log("TheIntroDB v4 response/cache error: {}".format(exc), "warning")
            return self._read_cache(cache_path, allow_stale=True)

    @staticmethod
    def get_ranges_from_data(data, segment_type, duration_seconds=0):
        """Preserve every valid range; normalize documented null boundaries safely."""
        if not isinstance(data, dict):
            return []
        raw = data.get(segment_type)
        if isinstance(raw, dict):
            raw = [raw]
        if not isinstance(raw, list):
            return []
        try:
            duration = float(duration_seconds or 0)
        except (TypeError, ValueError, OverflowError):
            duration = 0.0
        ranges = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            start_ms = item.get("start_ms")
            end_ms = item.get("end_ms")
            if start_ms is None:
                if segment_type in ("intro", "recap"):
                    start = 0.0
                else:
                    continue
            else:
                try:
                    start = float(start_ms) / 1000.0
                except (TypeError, ValueError, OverflowError):
                    continue
            if end_ms is None:
                if segment_type in ("credits", "preview") and duration > 0:
                    end = duration
                else:
                    continue
            else:
                try:
                    end = float(end_ms) / 1000.0
                except (TypeError, ValueError, OverflowError):
                    continue
            if (start < 0 or end <= start or end >= 86400
                    or (duration > 0 and (start >= duration or end > duration + 5))):
                continue
            end = min(end, duration) if duration > 0 else end
            ranges.append((start, end))
        # Duplicate ranges can appear when different submissions normalize to
        # the same boundary. Keep every distinct interval, in playback order.
        unique = {}
        for start, end in ranges:
            unique[(round(start, 3), round(end, 3))] = (start, end)
        return [unique[key] for key in sorted(unique)]

    @staticmethod
    def evidence_for(data, segment_type, duration_ms=0):
        raw = data.get(segment_type) if isinstance(data, dict) else None
        if isinstance(raw, dict):
            raw = [raw]
        if not isinstance(raw, list):
            raw = []
        confidence_values = []
        submissions = 0
        for item in raw:
            if not isinstance(item, dict):
                continue
            confidence = item.get("confidence")
            if confidence is None:
                confidence = item.get("confidence_score")
            if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
                confidence_values.append(float(confidence))
            count = item.get("submission_count", item.get("submissionCount", 0))
            try:
                submissions = max(submissions, int(count or 0))
            except (TypeError, ValueError, OverflowError):
                pass
        group_duration = data.get("group_duration_ms", data.get("groupDurationMs"))
        version_match = False
        try:
            if duration_ms and group_duration:
                version_match = abs(int(group_duration) - int(duration_ms)) <= max(30000, int(duration_ms) * 0.03)
        except (TypeError, ValueError, OverflowError):
            pass
        return {
            "source": "theintrodb",
            "confidence": max(confidence_values) if confidence_values else None,
            "submissions": submissions,
            "version_match": version_match,
            "provider": "TheIntroDB v4",
        }
