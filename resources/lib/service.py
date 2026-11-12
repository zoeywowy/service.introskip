# -*- coding: utf-8 -*-
"""Kodi background service presenting a shared skip prompt for each segment."""

import xbmc
import time
import xbmcgui
import xbmcvfs

from resources.lib import settings, tools
from resources.lib.player import Player
from resources.lib.segment_policy import validate_range, can_auto_skip
from resources.lib.kodi_native import KodiNativeMonitor

_addon_data = xbmcvfs.translatePath(settings.get_addon_info('profile'))

ORDER = ('recap', 'intro', 'outro', 'movie_outro')
MODE_SETTINGS = {
    'intro': 'skip.intro_mode',
    'recap': 'skip.recap_mode',
    'outro': 'skip.outro_mode',
    'movie_outro': 'skip.movie_outro_mode',
}
ENABLE_SETTINGS = {
    'intro': 'general.use_intro',
    'recap': 'general.use_recap',
    'outro': 'general.use_outro',
    'movie_outro': 'general.use_movie_credits',
}


def _enabled(kind):
    key = ENABLE_SETTINGS.get(kind)
    return not key or settings.get_setting_boolean(key)


def _mode(kind):
    try:
        return 'auto' if int(settings.get_setting(MODE_SETTINGS[kind]) or '0') == 1 else 'ask'
    except (TypeError, ValueError, OverflowError, KeyError):
        return 'ask'


def _close(dialog):
    try:
        dialog.close()
    except Exception:
        pass


def run():
    tools.log('Service starting...', 'info')
    # Legacy versions saved localized IDs rather than the labelenum value.
    # Normalize once so Kodi's conditional Light/Dark color selectors work.
    legacy_theme = settings.get_setting('customize.theme')
    if legacy_theme in ('32002', '32003'):
        settings.set_setting('customize.theme', 'Light' if legacy_theme == '32002' else 'Dark')
    monitor = KodiNativeMonitor()
    player = Player()
    tools.create_folder(_addon_data)
    file_key = None
    generation = player.playback_generation
    handled = set()
    active_kind = None
    chapter_probe_at = None
    chapter_probe_count = 0
    native_probe_count = 0
    native_probe_at = 0.0

    while not monitor.abortRequested():
        if monitor.waitForAbort(0.5):
            break
        try:
            is_playing = player.isPlayingVideo()
        except Exception:
            is_playing = False
        if not is_playing:
            if file_key is not None or active_kind:
                _close(player.get_dialog())
            file_key = None
            handled.clear()
            active_kind = None
            chapter_probe_at = None
            chapter_probe_count = 0
            native_probe_count = 0
            native_probe_at = 0.0
            monitor.take_changes()
            continue

        try:
            playing_file = player.getPlayingFile() or xbmc.getInfoLabel('Player.Filenameandpath') or None
        except Exception:
            playing_file = None
        if playing_file != file_key or player.playback_generation != generation:
            _close(player.get_dialog())
            file_key = playing_file
            generation = player.playback_generation
            handled.clear()
            active_kind = None
            chapter_probe_at = time.monotonic()
            chapter_probe_count = 0
            native_probe_count = 0
            native_probe_at = 0.0
            monitor.take_changes()

        try:
            now = float(player.getTime())
            duration = float(player.getTotalTime() or 0)
        except (ValueError, TypeError, RuntimeError):
            continue

        # Kodi 22 can report when chapter metadata changes. Refresh missing
        # matches on the service thread (never in the
        # Kodi notification callback). Scheduled probes below remain enabled.
        changes = monitor.take_changes()
        if changes and native_probe_count < 3 and time.monotonic() - native_probe_at >= 2.0:
            native_probe_at = time.monotonic()
            native_probe_count += 1
            if 'chapters' in changes:
                tools.log('Kodi native event: chapter properties changed', 'info')
                try:
                    player.refresh_chapter_segments(force=True)
                except Exception as exc:
                    tools.log('Chapter event refresh failed: {}'.format(exc), 'warning')
        # Kodi streams can populate chapter markers a few seconds after AV start.
        # Poll only three times, without invoking network-based detectors.
        if (chapter_probe_at is not None and chapter_probe_count < 3
                and not player.chapters_ready()
                and getattr(player, '_media_type', None) in ('episode', 'movie')):
            age = time.monotonic() - chapter_probe_at
            if age >= (2.5, 6.0, 12.0)[chapter_probe_count]:
                chapter_probe_count += 1
                try:
                    tools.log('Kodi chapter delayed probe {}/3 at {:.1f}s after playback'.format(
                        chapter_probe_count, age), 'info')
                    player.refresh_chapter_segments(force=True)
                except Exception as exc:
                    tools.log('Deferred Kodi chapter check failed: {}'.format(exc), 'warning')

        # Network work finishes independently; apply results on service thread.
        player.apply_ready_network_results()

        notification = player.take_detection_notification()
        if notification and settings.get_setting_boolean('general.show_notifications'):
            tools.show_notification(notification, time=2800)

        segments = player.get_segments()
        dialog = player.get_dialog()
        if active_kind:
            current = validate_range(segments.get(active_kind), duration)
            # Dismissal/skip affects only the current segment, not future ones.
            if current:
                try:
                    old_end = float(dialog.getProperty('skip_time') or 0)
                    if abs(current[1] - old_end) > 0.25:
                        dialog.setProperty('skip_time', str(current[1]))
                        tools.log('Updated active {} button target from {:.2f}s to {:.2f}s'.format(
                            active_kind, old_end, current[1]), 'info')
                except (ValueError, TypeError, OverflowError, RuntimeError):
                    pass
            if dialog.isCancelled():
                handled.add(active_kind)
                _close(dialog)
                active_kind = None
            elif not current or now >= current[1] or not _enabled(active_kind):
                handled.add(active_kind)
                _close(dialog)
                active_kind = None
            elif now < current[0] - 2:
                # User sought backward; allow the prompt when returning to this range.
                _close(dialog)
                active_kind = None
            else:
                continue

        for kind in ORDER:
            if kind in handled or not _enabled(kind):
                continue
            bounds = validate_range(segments.get(kind), duration)
            if not bounds:
                continue
            start, end = bounds
            if now >= end:
                handled.add(kind)
                continue
            if not (start <= now < end):
                continue

            evidence = player.evidence_for(kind)
            auto_allowed = can_auto_skip(_mode(kind), evidence.get('source'),
                                         evidence.get('confidence'), evidence.get('submissions'))
            # IntroDB does not confirm that a film lacks post-credit scenes.
            # Without an identified post-credit interval, require a manual prompt.
            if kind == 'movie_outro' and not player.post_credits:
                auto_allowed = False
            if auto_allowed:
                # Source-local variations can invalidate reference timings.
                # Automatic skipping is off by default and never uses guesses.
                try:
                    if end - 1.0 > now:
                        player.seekTime(max(0.0, end - 1.0))
                        player.reset_segment(kind)
                        handled.add(kind)
                        tools.log('Automatically skipped {}'.format(kind), 'info')
                        break
                except Exception as exc:
                    tools.log('Automatic seek failed for {}: {}'.format(kind, exc), 'warning')
                # Keep the normal prompt available if seeking fails.

            try:
                active_dialog = xbmcgui.getCurrentWindowDialogId()
            except Exception:
                active_dialog = 0
            if active_dialog and active_dialog >= 13000:
                # Do not overlay other modal dialogs or configuration windows.
                break
            try:
                dialog.configure(kind, end)
                dialog.show()
                active_kind = kind
            except Exception as exc:
                tools.log('Could not show {} prompt: {}'.format(kind, exc), 'warning')
            break

    _close(player.get_dialog())
