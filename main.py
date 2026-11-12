# -*- coding: utf-8 -*-
"""IntroSkip script entry point for Kodi settings and small actions."""

import sys

import xbmcaddon


def _parse_arguments(arguments):
    """Parse Kodi RunScript arguments without assuming a fixed format."""
    params = {}
    for argument in arguments:
        if not isinstance(argument, str) or "=" not in argument:
            continue
        key, value = argument.split("=", 1)
        params[key.strip()] = value.strip()
    return params


def run(arguments=None):
    params = _parse_arguments(sys.argv[1:] if arguments is None else arguments)
    action = params.get("action")

    if action == "reset_button_layout":
        import xbmcgui
        if xbmcgui.Dialog().yesno('IntroSkip', 'Restore the default button theme, color, layout, and size?'):
            addon = xbmcaddon.Addon()
            for key, value in (
                ('customize.position', '0'), ('customize.size', '1'),
                ('customize.style', '0'), ('customize.contents', '0'),
                ('customize.theme', 'Dark'), ('customize.button_color', '0'),
                ('customize.button_color_light', '0'),
            ):
                addon.setSetting(key, value)
        return

    if action == "preview_button":
        import xbmcvfs
        from resources.lib.skip_dialog import IntroSkipDialog
        addon_path = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('path'))
        dialog = IntroSkipDialog('intro_skip_dialog.xml', addon_path, 'Default', '1080i')
        dialog.preview_mode = True
        dialog.configure('intro', 0)
        try:
            dialog.doModal()
        finally:
            del dialog
        # Preview is launched after Kodi saves and closes the settings dialog.
        # Bring settings back so users can adjust and preview again by remote.
        xbmcaddon.Addon().openSettings()
        return

    # Opening the add-on from Kodi's Programs/Add-ons screen opens settings.
    xbmcaddon.Addon().openSettings()


if __name__ == "__main__":
    run()
