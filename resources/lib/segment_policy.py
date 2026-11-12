# -*- coding: utf-8 -*-
"""Small, Kodi-independent safeguards shared by all skip segment types."""
import math
import re

SEGMENT_LABELS = {
    'recap': 'Skip Recap',
    'intro': 'Skip Intro',
    'outro': 'Skip Credits',
    'movie_outro': 'Skip Movie Credits',
}


def validate_range(points, duration=0):
    """Return (start,end) in seconds or None; never manufacture times."""
    if not isinstance(points, (tuple, list)) or len(points) != 2:
        return None
    for value in points:
        if value is None or isinstance(value, bool):
            return None
        if isinstance(value, (int, float)) and not math.isfinite(float(value)):
            return None
        if isinstance(value, str) and not re.fullmatch(r"\d+(?::\d+){0,2}(?:\.\d+)?", value.strip()):
            return None
    try:
        from resources.lib.tools import convert_time_to_seconds
        start = float(convert_time_to_seconds(points[0]))
        end = float(convert_time_to_seconds(points[1]))
        duration = float(duration or 0)
    except (TypeError, ValueError, OverflowError, AttributeError):
        return None
    if not math.isfinite(start) or not math.isfinite(end):
        return None
    if start < 0 or end <= start or end >= 86400:
        return None
    if math.isfinite(duration) and duration > 0:
        if start >= duration or end > duration + 5:
            return None
        end = min(end, duration)
    return (start, end)


def stop_before_postcredits(credits, postcredits):
    """Never seek through a known post-credits scene."""
    if not credits or not postcredits:
        return credits
    start, end = credits
    post_start, _ = postcredits
    if start < post_start < end:
        return (start, post_start)
    # A scene starts before (or at) the identified credits; don't suggest skipping.
    if post_start <= start:
        return None
    return credits


def can_auto_skip(mode, source=None, confidence=None, submissions=None):
    """Automatic seeking requires opt-in and a trustworthy known source."""
    if mode != 'auto':
        return False
    # Auto is an explicit opt-in, not a hidden minimum-vote filter.
    # Kodi's source may be a different edit, so leave all heuristic
    # chapter candidates in confirmation-only mode.
    return source == 'introdb'
