# -*- coding: utf-8 -*-
"""High-legibility button color shades for Kodi's light and dark themes.

The color selector is a normal enum setting, not an action script + hidden
text field. This avoids settings-dialog writeback races and makes the
selected shade visible in Kodi's settings screen.
"""
from resources.lib import settings

COLOR_NAMES = ('Default', 'Blue', 'Green', 'Gold', 'Red', 'Purple', 'Teal')
COLOR_VALUES = {
    'dark': (
        '0xFFF8FAFC', '0xFFA5D8FF', '0xFFB6F0CB', '0xFFFFE08A',
        '0xFFFFADB5', '0xFFD9B8FF', '0xFFA4E8E4',
    ),
    'light': (
        '0xFF18212C', '0xFF174A8B', '0xFF15603D', '0xFF7B4700',
        '0xFF9F2330', '0xFF5F358C', '0xFF005C64',
    ),
}


def current_theme():
    value = (settings.get_setting('customize.theme') or '').strip().casefold()
    localized_light = (settings.get_localized_string(32002) or 'Light').strip().casefold()
    return 'light' if value in ('light', '32002', localized_light) else 'dark'


def readable_color(value=None, theme=None):
    """Return Kodi's 0xAARRGGBB color for selected basic color and theme."""
    theme = theme if theme in COLOR_VALUES else current_theme()
    if value is None:
        key = 'customize.button_color_light' if theme == 'light' else 'customize.button_color'
        value = settings.get_setting(key)
    try:
        index = int(value)
    except (TypeError, ValueError, OverflowError):
        index = 0
    if not 0 <= index < len(COLOR_NAMES):
        index = 0
    return COLOR_VALUES[theme][index]
