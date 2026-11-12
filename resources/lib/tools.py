# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import xbmc
import xbmcvfs

import json
import math
import os
import re
import shutil
import sys
from xml.etree import ElementTree

from resources.lib import settings

_addon_id = settings.get_addon_info("id")

_log_levels = {
    "debug": xbmc.LOGDEBUG,
    "info": xbmc.LOGINFO,
    "warning": xbmc.LOGWARNING,
    "error": xbmc.LOGERROR,
    "fatal": xbmc.LOGFATAL,
}


def sleep(ms):
    xbmc.sleep(ms)


def kodi_version():
    """Return Kodi's major version without assuming a fixed label format."""
    version = xbmc.getInfoLabel("System.BuildVersion") or ""
    match = re.match(r"\s*(\d+)", version)
    return int(match.group(1)) if match else 0


def remove_folder(path):
    if xbmcvfs.exists(ensure_path_is_dir(path)):
        log("Removing {}".format(path))
        try:
            shutil.rmtree(path)
        except Exception as e:
            log("Error removing {}: {}".format(path, e))


def remove_file(path):
    if xbmcvfs.exists(path):
        log("Removing {}".format(path))
        try:
            os.remove(path)
        except Exception as e:
            log("Error removing {}: {}".format(path, e))


def read_from_file(file_path):
    try:
        with xbmcvfs.File(file_path, "r") as f:
            content = f.read()
        return content
    except IOError:
        return None


def write_to_file(file_path, content):
    try:
        with xbmcvfs.File(file_path, "w") as f:
            success = f.write(content)
        return success
    except IOError:
        return None


def read_json(file_path):
    content = read_from_file(file_path)
    if not content:
        return None
    try:
        return json.loads(content)
    except (TypeError, ValueError) as exc:
        log("Could not read JSON from file {}: {}".format(file_path, exc), level="error")
        return None


def write_json(file_path, json_object):
    return write_to_file(file_path, json.dumps(json_object))


def parse_xml(file=None, text=None):
    if (file and text) or not (file or text):
        raise ValueError("Incorrect parameters for parsing.")
    if file and not text:
        text = read_from_file(file)
    if not text:
        return None

    try:
        return ElementTree.fromstring(text.strip())
    except ElementTree.ParseError as exc:
        log("Error parsing XML: {}".format(exc), level="error")
        return None


def log(msg, level="debug"):
    xbmc.log("[ {} ] {}".format(_addon_id, msg), level=_log_levels[level])
    

def show_notification(message, time=4500, icon=None):
    """Native Kodi notification, no forced sound; works on Android TV/Fire TV."""
    import xbmcgui
    heading = settings.get_addon_info('name') or 'IntroSkip'
    if icon is None:
        icon = settings.get_addon_info('icon') or xbmcgui.NOTIFICATION_INFO
    try:
        xbmcgui.Dialog().notification(heading, str(message), icon, int(time), False)
        log('Detection notification: {}'.format(message), 'info')
        return True
    except Exception as exc:
        log('Native detection notification failed: {}'.format(exc), 'warning')
        return False


def seconds_to_time(seconds):
    """Convert finite seconds to a ``datetime.time`` without losing fractions."""
    from datetime import time
    if isinstance(seconds, bool):
        return None
    try:
        seconds = float(seconds)
    except (TypeError, ValueError, OverflowError):
        return None
    if not math.isfinite(seconds) or seconds < 0 or seconds >= 86400:
        return None

    total_microseconds = int(round(seconds * 1000000))
    hours, remainder = divmod(total_microseconds, 3600 * 1000000)
    minutes, remainder = divmod(remainder, 60 * 1000000)
    whole_seconds, microseconds = divmod(remainder, 1000000)
    try:
        return time(int(hours), int(minutes), int(whole_seconds), int(microseconds))
    except ValueError:
        return None


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



def ensure_path_is_dir(path):
    """Return a directory path with the platform's preferred trailing slash."""
    path = str(path or "")
    if sys.platform == "win32":
        return path.rstrip("\\/") + "\\" if path else "\\"
    return path.rstrip("/") + "/" if path else "/"


def create_folder(path):
    path = ensure_path_is_dir(path)
    if not xbmcvfs.exists(path):
        xbmcvfs.mkdir(path)


def get_condition(condition):
    return xbmc.getCondVisibility(condition)


def execute_builtin(bi):
    xbmc.executebuiltin(bi)


def execute_jsonrpc(method, params=None):
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
            "JsonRPC Error {}: {}".format(error.get("code", "?"), error.get("message", "Unknown error")),
            "debug",
        )
    # JSON-RPC methods do not all return dictionaries. For example,
    # Player.GetActivePlayers returns a list, which the chapter detector needs.
    # Preserve the result's native JSON type instead of silently discarding lists.
    return response.get("result", {})


def levenshteinDistanceDP(token1, token2):
    distances = [[0] * (len(token2) + 1) for _ in range(len(token1) + 1)]

    for t1 in range(len(token1) + 1):
        distances[t1][0] = t1

    for t2 in range(len(token2) + 1):
        distances[0][t2] = t2

    a = 0
    b = 0
    c = 0

    for t1 in range(1, len(token1) + 1):
        for t2 in range(1, len(token2) + 1):
            if token1[t1 - 1] == token2[t2 - 1]:
                distances[t1][t2] = distances[t1 - 1][t2 - 1]
            else:
                a = distances[t1][t2 - 1]
                b = distances[t1 - 1][t2]
                c = distances[t1 - 1][t2 - 1]

                if a <= b and a <= c:
                    distances[t1][t2] = a + 1
                elif b <= a and b <= c:
                    distances[t1][t2] = b + 1
                else:
                    distances[t1][t2] = c + 1

    return distances[len(token1)][len(token2)]