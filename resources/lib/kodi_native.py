# -*- coding: utf-8 -*-
"""Kodi 22 chapter-change event bridge, implemented with public Python APIs.

Kodi may notify add-ons of player property changes. The service processes only
chapter-related notifications, off the callback thread. Periodic chapter
probes remain the fallback for sources that do not send notifications.
"""
import json

import xbmc


class KodiNativeMonitor(xbmc.Monitor):
    """Queue chapter metadata changes for the service's main loop."""

    def __init__(self):
        super().__init__()
        self._pending = set()

    def onNotification(self, sender, method, data):
        if method != 'Player.OnPropertyChanged':
            return
        try:
            payload = json.loads(data) if isinstance(data, str) else data
        except (TypeError, ValueError):
            return
        if not isinstance(payload, dict):
            return
        changed = payload.get('property', {})
        if isinstance(changed, dict):
            keys = [str(key).lower() for key in changed]
            if isinstance(changed.get('name'), str):
                keys.append(changed['name'].lower())
        elif isinstance(changed, str):
            keys = [changed.lower()]
        else:
            return
        if any('chapter' in key for key in keys):
            self._pending.add('chapters')

    def take_changes(self):
        changes = set(self._pending)
        self._pending.clear()
        return changes
