# -*- coding: utf-8 -*-
"""Select bundled modern PNG button textures."""
from __future__ import absolute_import
import os

SIZES = ((196, 82), (248, 104), (320, 128))


def button_layout(position, size):
    """Keep prompts away from subtitle and transport-control regions."""
    try:
        position = int(position)
    except (TypeError, ValueError):
        position = 0
    try:
        size = int(size)
    except (TypeError, ValueError):
        size = 1
    position = min(3, max(0, position))
    size = min(2, max(0, size))
    width, height = SIZES[size]
    x = 1920 - width - 32 if position in (0, 2) else 32
    y = 1080 - height - 288 if position in (0, 1) else 72
    return x, y, width, height


def textures(media_path, theme='dark', style=0):
    theme = 'light' if str(theme).lower() in ('light', '32002') else 'dark'
    try:
        style = min(max(0, int(style)), 2)
    except (TypeError, ValueError):
        style = 0
    style_name = ('pill', 'soft', 'flat')[style]
    prefix = 'modern_{}_{}'.format(theme, style_name)
    return (
        os.path.join(media_path, prefix + '_focus.png'),
        os.path.join(media_path, prefix + '_normal.png')
    )
