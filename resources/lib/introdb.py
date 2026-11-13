# -*- coding: utf-8 -*-
"""IntroDB episode adapter; does not cache timestamps across playbacks."""

import math
from datetime import time

from resources.lib.adapter import PointsAdapter
from resources.lib import http_client, tools


class IntroDBAdapter(PointsAdapter):
    """Fetch community-submitted intro, recap, and outro timestamps."""

    BASE_URL = "https://api.introdb.app/segments"

    def __init__(self, timeout=3):
        self.timeout = timeout

    def get_episode_data(self, imdb, season, episode):
        """Make one remote request when playback needs this episode's data."""
        imdb_id = str(imdb or '').strip().lower()
        if not imdb_id.startswith('tt') or not imdb_id[2:].isdigit():
            return None
        try:
            season, episode = int(season), int(episode)
        except (ValueError, TypeError, OverflowError):
            return None
        if season < 1 or episode < 1:
            return None
        return self._fetch_episode(imdb_id, season, episode)

    def get_movie_data(self, imdb):
        """Fetch movie credits; no persistent or cross-episode timestamp cache."""
        imdb_id = str(imdb or '').strip().lower()
        if not imdb_id.startswith('tt') or not imdb_id[2:].isdigit():
            return None
        try:
            data = http_client.get_json(self.BASE_URL, params={
                'imdb_id': imdb_id, 'is_movie': 'true'}, timeout=self.timeout)
        except (http_client.HTTPError, ValueError, TypeError) as exc:
            tools.log('IntroDB movie lookup failed: {}'.format(exc), 'warning')
            return None
        return data if isinstance(data, dict) else None

    def get_points(self, imdb, season, episode, type=None):
        """Return ``[(start_time, end_time)]`` for the requested segment."""
        segment_type = type or "intro"
        data = self.get_episode_data(imdb, season, episode)
        return self.get_points_from_data(data, segment_type)

    def get_all_points_from_data(self, data, segment_type):
        """Return every valid interval in a live API response or open-data row set."""
        if segment_type not in ("intro", "recap", "outro", "post_credits"):
            tools.log("Unsupported IntroDB segment type: {}".format(segment_type), "warning")
            return []
        if not isinstance(data, dict):
            return []
        raw = data.get("post_credits" if segment_type == "post_credits" else segment_type)
        if isinstance(raw, dict):
            raw = [raw]
        if not isinstance(raw, list):
            return []

        ranges = []
        for segment_data in raw:
            if not isinstance(segment_data, dict):
                continue
            start_value = segment_data.get("start_sec")
            end_value = segment_data.get("end_sec")
            if start_value is None and segment_data.get("start_ms") is not None:
                start_value = self._to_seconds(segment_data.get("start_ms"))
                if start_value is not None:
                    start_value /= 1000.0
            if end_value is None and segment_data.get("end_ms") is not None:
                end_value = self._to_seconds(segment_data.get("end_ms"))
                if end_value is not None:
                    end_value /= 1000.0

            start_seconds = self._to_seconds(start_value)
            end_seconds = self._to_seconds(end_value)
            if (start_seconds is None or end_seconds is None or start_seconds < 0
                    or end_seconds <= start_seconds or end_seconds >= 86400):
                tools.log("IntroDB returned an invalid {} range".format(segment_type), "warning")
                continue
            start = self._to_time(start_seconds)
            end = self._to_time(end_seconds)
            if start is not None and end is not None:
                ranges.append((start, end))

        unique = {}
        for start, end in ranges:
            key = (self._to_seconds(start), self._to_seconds(end))
            unique[key] = (start, end)
        result = [unique[key] for key in sorted(unique)]
        if result:
            details = []
            confidence_values = [
                item.get("confidence") for item in raw
                if isinstance(item, dict) and isinstance(item.get("confidence"), (int, float))
                and not isinstance(item.get("confidence"), bool)
            ]
            submission_values = [
                item.get("submission_count") for item in raw
                if isinstance(item, dict) and isinstance(item.get("submission_count"), int)
            ]
            if confidence_values:
                details.append("confidence: {:.0%}".format(max(confidence_values)))
            if submission_values:
                details.append("submissions: {}".format(max(submission_values)))
            tools.log(
                "IntroDB {}: {} interval(s){}".format(
                    segment_type, len(result),
                    " ({})".format(", ".join(details)) if details else ""
                ),
                "info",
            )
        return result

    def get_points_from_data(self, data, segment_type):
        """Backward-compatible first interval accessor."""
        points = self.get_all_points_from_data(data, segment_type)
        return points[0] if points else None

    @staticmethod
    def is_confirmed_absent_from_data(data, segment_type):
        """Whether IntroDB's community has explicitly confirmed no segment."""
        if not isinstance(data, dict) or segment_type not in ("intro", "recap", "outro"):
            return False
        return data.get("no_{}".format(segment_type)) is True

    def _fetch_episode(self, imdb_id, season, episode):
        params = {
            "imdb_id": imdb_id,
            "season": season,
            "episode": episode,
        }
        try:
            data = http_client.get_json(self.BASE_URL, params=params, timeout=self.timeout)
        except requests.exceptions.RequestException as exc:
            tools.log("IntroDB request failed: {}".format(exc), "warning")
            return None
        except (ValueError, TypeError) as exc:
            tools.log("IntroDB returned invalid JSON: {}".format(exc), "warning")
            return None

        if not isinstance(data, dict):
            tools.log("IntroDB returned an unexpected response format", "warning")
            return None
        tools.log(
            "IntroDB response received for {} S{}E{}".format(imdb_id, season, episode),
            "debug",
        )
        return data

    @staticmethod
    def _to_seconds(value):
        """Convert API timestamps to finite seconds without losing fractions."""
        if isinstance(value, bool) or value is None:
            return None
        try:
            if isinstance(value, str) and ":" in value:
                parts = value.strip().split(":")
                if len(parts) == 3:
                    seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                elif len(parts) == 2:
                    seconds = int(parts[0]) * 60 + float(parts[1])
                else:
                    return None
            else:
                seconds = float(value)
        except (TypeError, ValueError, OverflowError):
            return None
        return seconds if math.isfinite(seconds) else None

    @staticmethod
    def _to_time(seconds):
        """Convert seconds to datetime.time while retaining millisecond precision."""
        seconds = IntroDBAdapter._to_seconds(seconds)
        if seconds is None or seconds < 0 or seconds >= 86400:
            return None

        total_microseconds = int(round(seconds * 1000000))
        hours, remainder = divmod(total_microseconds, 3600 * 1000000)
        minutes, remainder = divmod(remainder, 60 * 1000000)
        whole_seconds, microseconds = divmod(remainder, 1000000)
        try:
            return time(int(hours), int(minutes), int(whole_seconds), int(microseconds))
        except ValueError:
            return None
