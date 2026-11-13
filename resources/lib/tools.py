# -*- coding: utf-8 -*-
"""Small Kodi helpers used by playback, chapters and the skip prompt."""
from __future__ import absolute_import, division, unicode_literals

import json
import math

import xbmc

from resources.lib import settings


_addon_id = settings.get_addon_info("id")

_log_levels = {
    "debug": xbmc.LOGDEBUG,
    "info": xbmc.LOGINFO,
    "warning": xbmc.LOGWARNING,
    "error": xbmc.LOGERROR,
    "fatal": xbmc.LOGFATAL,
}


def log(msg, level="debug"):
    xbmc.log("[ {} ] {}".format(_addon_id, msg), level=_log_levels[level])


def show_notification(message, time=4500, icon=None):
    """Use Kodi's native notification without forcing a sound."""
    import xbmcgui

    heading = settings.get_addon_info("name") or "IntroSkip"
    if icon is None:
        icon = settings.get_addon_info("icon") or xbmcgui.NOTIFICATION_INFO
    try:
        xbmcgui.Dialog().notification(heading, str(message), icon, int(time), False)
        log("Detection notification: {}".format(message), "info")
        return True
    except Exception as exc:
        log("Native detection notification failed: {}".format(exc), "warning")
        return False


def convert_time_to_seconds(time_obj):
    """Convert Kodi time values to finite seconds; invalid values safely become 0."""
    if time_obj is None or isinstance(time_obj, bool):
        return 0.0

    if isinstance(time_obj, (int, float)):
        value = float(time_obj)
        return value if math.isfinite(value) else 0.0

    if all(hasattr(time_obj, part) for part in ("hour", "minute", "second")):
        try:
            value = (
                int(time_obj.hour) * 3600
                + int(time_obj.minute) * 60
                + int(time_obj.second)
                + getattr(time_obj, "microsecond", 0) / 1000000.0
            )
            return value if math.isfinite(value) else 0.0
        except (TypeError, ValueError, OverflowError):
            return 0.0

    if isinstance(time_obj, str):
        value = time_obj.strip()
        if not value:
            return 0.0
        try:
            parsed = float(value)
            return parsed if math.isfinite(parsed) else 0.0
        except ValueError:
            parts = value.split(":")
            try:
                if len(parts) == 3:
                    parsed = int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                elif len(parts) == 2:
                    parsed = int(parts[0]) * 60 + float(parts[1])
                else:
                    return 0.0
                return parsed if math.isfinite(parsed) else 0.0
            except (TypeError, ValueError, OverflowError):
                return 0.0

    try:
        parsed = float(time_obj)
        return parsed if math.isfinite(parsed) else 0.0
    except (TypeError, ValueError, OverflowError):
        return 0.0


def execute_jsonrpc(method, params=None):
    """Call Kodi JSON-RPC and preserve the result's native JSON type."""
    request_data = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": params or {},
    }
    try:
        raw_response = xbmc.executeJSONRPC(json.dumps(request_data))
        response = json.loads(raw_response) if raw_response else {}
    except (TypeError, ValueError) as exc:
        log("Invalid JSON-RPC response for {}: {}".format(method, exc), "warning")
        return {}
    except Exception as exc:
        log("JSON-RPC call {} failed: {}".format(method, exc), "warning")
        return {}

    if not isinstance(response, dict):
        log("JSON-RPC method {} returned an invalid response envelope".format(method), "warning")
        return {}

    if "error" in response:
        error = response.get("error") or {}
        log(
            "JsonRPC Error {}: {}".format(
                error.get("code", "?"), error.get("message", "Unknown error")
            ),
            "debug",
        )
    return response.get("result", {})
