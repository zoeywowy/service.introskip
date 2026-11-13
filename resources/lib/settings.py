# -*- coding: utf-8 -*-
"""Small cached wrapper around Kodi's add-on settings API."""
from __future__ import absolute_import, division, unicode_literals

import xbmcaddon


_DEFAULT_ADDON = None


def _get_addon(addon=None):
    """Reuse the current add-on wrapper in the frequently polled service loop."""
    global _DEFAULT_ADDON
    if addon:
        return xbmcaddon.Addon(addon)
    if _DEFAULT_ADDON is None:
        _DEFAULT_ADDON = xbmcaddon.Addon()
    return _DEFAULT_ADDON


def get_localized_string(_id, addon=None):
    return _get_addon(addon).getLocalizedString(_id)


def get_setting(setting, addon=None):
    return _get_addon(addon).getSetting(setting)


def get_setting_boolean(setting, addon=None):
    return _get_addon(addon).getSettingBool(setting)


def get_setting_int(setting, addon=None):
    return _get_addon(addon).getSettingInt(setting)


def get_setting_float(setting, addon=None):
    return _get_addon(addon).getSettingNumber(setting)


def get_setting_string(setting, addon=None):
    return _get_addon(addon).getSettingString(setting)


def set_setting(setting, value, addon=None):
    return _get_addon(addon).setSetting(setting, value)


def set_setting_boolean(setting, value, addon=None):
    return _get_addon(addon).setSettingBool(setting, value)


def set_setting_int(setting, value, addon=None):
    return _get_addon(addon).setSettingInt(setting, value)


def set_setting_float(setting, value, addon=None):
    return _get_addon(addon).setSettingNumber(setting, value)


def set_setting_string(setting, value, addon=None):
    return _get_addon(addon).setSettingString(setting, value)


def open_settings(addon=None):
    return _get_addon(addon).openSettings()


def get_addon_info(label, addon=None):
    return _get_addon(addon).getAddonInfo(label)
