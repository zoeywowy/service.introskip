# -*- coding: utf-8 -*-
"""Remote-controlled skip dialog using bundled modern PNG textures."""
import math
import os

import xbmc
import xbmcgui
import xbmcvfs

from resources.lib import settings, tools
from resources.lib.segment_policy import SEGMENT_LABELS
from resources.lib.button_assets import button_layout, textures

ACTION_PREVIOUS_MENU = 10
ACTION_BACK = 92
FALLBACK_BUTTON = 201


def _choice(key, default=0, maximum=3):
    try:
        value = int(settings.get_setting(key) or str(default))
    except (ValueError, TypeError, OverflowError):
        value = default
    return min(max(0,value),maximum)


from resources.lib.color import current_theme, readable_color


class IntroSkipDialog(xbmcgui.WindowXMLDialog):
    def __init__(self, xmlFilename, scriptPath, defaultSkin='Default', defaultRes='720p', player=None):
        super().__init__(xmlFilename, scriptPath, defaultSkin, defaultRes)
        self.player=player
        self._cancelled=False
        self.segment_type='intro'
        self.skip_time=0
        self.skip_start=0
        self.preview_mode=False
        self._button=None
        self._icon=None
        self._button_id=None

    def configure(self, segment_type, skip_time, skip_start=None):
        self.segment_type=segment_type if segment_type in SEGMENT_LABELS else 'intro'
        self.skip_time=skip_time
        self.skip_start=skip_start if skip_start is not None else 0
        self._cancelled=False
        self.setProperty('skip_time',str(skip_time))
        self.setProperty('skip_type',self.segment_type)
        self.setProperty('skip.label',SEGMENT_LABELS[self.segment_type])
        self.setProperty('cancelled','False')

    def onInit(self):
        self._cancelled=False
        try:
            self._configure_png_button(current_theme())
        except Exception as exc:
            tools.log('PNG button setup failed, keeping original button: {}'.format(exc),'error')
            # No visible XML placeholder: never flash at the wrong size/location.
            try:
                x,y,w,h=button_layout(_choice('customize.position',0,3),
                                      _choice('customize.size',1,2))
                label=SEGMENT_LABELS.get(self.segment_type, 'Skip Intro')
                self._button=xbmcgui.ControlButton(x,y,w,h,label,alignment=2|4|8)
                self.addControl(self._button)
                self._button_id=self._button.getId()
                self.setFocus(self._button)
            except Exception:
                pass

    def _remove_custom_controls(self):
        for control in (self._icon,self._button):
            if control is not None:
                try:
                    self.removeControl(control)
                except Exception:
                    pass
        self._icon=None
        self._button=None
        self._button_id=None

    def _configure_png_button(self,theme):
        self._remove_custom_controls()
        x,y,w,h=button_layout(_choice('customize.position',0,3),_choice('customize.size',1,2))
        size=_choice('customize.size',1,2)
        style=_choice('customize.style',0,2)
        contents=_choice('customize.contents',0,2)
        media_path=os.path.join(xbmcvfs.translatePath(settings.get_addon_info('path')),'resources','skins','Default','media')
        focus_texture, normal_texture=textures(media_path,theme,style)
        # Short labels + XBFONT_TRUNCATED prevent the scrolling marquee loop.
        label = 'Skip Credits' if self.segment_type == 'movie_outro' else SEGMENT_LABELS.get(self.segment_type, 'Skip Intro')
        if size == 0 and contents == 0:
            label = {'intro':'Intro', 'recap':'Recap', 'preview':'Preview',
                     'outro':'Credits', 'movie_outro':'Credits'}.get(self.segment_type, 'Skip')
        text = label if contents != 2 else '' 
        text_color=readable_color(theme=theme)
        # Kodi directly constructs this focusable button with bundled PNG textures.
        # Kodi XBFONT_TRUNCATED (0x08) prevents "Skip Intro | Skip Intro" looping.
        alignment=(4 | 8) if contents==0 else (2 | 4 | 8)
        icon_size=(28,36,42)[size]
        button_text_offset=(14,24,34)[size] + icon_size + (10,12,14)[size] if contents==0 else 0
        button=xbmcgui.ControlButton(x,y,w,h,text,
           focusTexture=focus_texture,noFocusTexture=normal_texture,
           textOffsetX=button_text_offset,alignment=alignment,font='font12' if size==0 else 'font13',
           textColor=text_color,focusedColor=text_color)
        self.addControl(button)
        self._button=button
        self._button_id=button.getId()
        # The icon is already a real PNG from IntroSkip's existing artwork.
        if contents!=1:
            icon_x=x+(w-icon_size)//2 if contents==2 else x+(14,24,34)[size]
            icon_y=y+(h-icon_size)//2
            self._icon=xbmcgui.ControlImage(icon_x,icon_y,icon_size,icon_size,
                   os.path.join(media_path,'skip-next.png'),aspectRatio=2,
                   colorDiffuse=text_color)
            self.addControl(self._icon)
        self.setFocus(button)
        tools.log('Modern button active: {} at {},{} size {}x{} style={} mode={} theme={} text_color={}'.format(
            self.segment_type, x, y, w, h, style, contents, theme, text_color), 'info')

    def onAction(self,action):
        action_id=action.getId() if hasattr(action,'getId') else action
        if action_id in (ACTION_PREVIOUS_MENU,ACTION_BACK):
            self._cancelled=True
            self.setProperty('cancelled','True')
            self.close()

    def onClick(self,control):
        if control not in (FALLBACK_BUTTON,self._button_id):
            return
        if self.preview_mode:
            self._cancelled=True
            self.close()
            return
        try:
            end=float(self.getProperty('skip_time') or self.skip_time)
        except (TypeError,ValueError,OverflowError):
            return
        if not math.isfinite(end) or end<=0:
            return
        player=self.player or xbmc.Player()
        try:
            player.seekTime(max(0.0,end-1.0))
        except Exception as exc:
            tools.log('Could not seek to end of {}: {}'.format(self.segment_type,exc),'warning')
            return
        self._cancelled=True
        self.setProperty('cancelled','True')
        if self.player:
            bounds = (self.skip_start, end) if self.skip_start is not None else None
            self.player.reset_segment(self.segment_type, bounds)
        self.close()

    def isCancelled(self):
        return self._cancelled
