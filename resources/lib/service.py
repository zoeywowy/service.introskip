# -*- coding: utf-8 -*-
"""Kodi background service presenting a shared skip prompt for each segment."""

import xbmc
import time
import xbmcgui

from resources.lib import settings, tools
from resources.lib.player import Player
from resources.lib.segment_policy import validate_range, can_auto_skip
from resources.lib.kodi_native import KodiNativeMonitor

OPEN_DATA_IDLE_DELAY = 120.0

ORDER = ('recap', 'intro', 'preview', 'outro', 'movie_outro')
MODE_SETTINGS = {
    'intro': 'skip.intro_mode',
    'recap': 'skip.recap_mode',
    'preview': 'skip.preview_mode',
    'outro': 'skip.outro_mode',
    'movie_outro': 'skip.movie_outro_mode',
}
ENABLE_SETTINGS = {
    'intro': 'general.use_intro',
    'recap': 'general.use_recap',
    'preview': 'general.use_preview',
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
    # The full IntroDB export is intentionally deferred until Kodi has been
    # idle without video playback for two minutes. Live API fallback remains
    # available immediately, so first-run installation never triggers a bulk import.
    sync_started = False
    idle_since = time.monotonic()
    was_playing = False
    file_key = None
    generation = player.playback_generation
    handled = set()
    active_key = None
    chapter_probe_at = None
    chapter_probe_count = 0
    native_probe_count = 0
    native_probe_at = 0.0

    try:
        while not monitor.abortRequested():
            if monitor.waitForAbort(0.5):
                break
            try:
                is_playing = player.isPlayingVideo()
            except Exception:
                is_playing = False

            clock_now = time.monotonic()
            if is_playing:
                if not was_playing:
                    was_playing = True
                    if sync_started:
                        # Do not compete with active playback. A cancelled sync
                        # can be retried cleanly on the next Kodi session.
                        player.identifier.introdb_open_data.cancel_sync()
            else:
                if was_playing:
                    idle_since = clock_now
                was_playing = False
                try:
                    ui_idle = float(xbmc.getGlobalIdleTime())
                except (AttributeError, TypeError, ValueError, RuntimeError):
                    ui_idle = 0.0
                if (not sync_started
                        and clock_now - idle_since >= OPEN_DATA_IDLE_DELAY
                        and ui_idle >= OPEN_DATA_IDLE_DELAY):
                    try:
                        player.identifier.introdb_open_data.start_background_sync()
                        sync_started = True
                    except Exception as exc:
                        tools.log('Could not start deferred IntroDB sync: {}'.format(exc), 'warning')
            if not is_playing:
                if file_key is not None or active_key:
                    _close(player.get_dialog())
                file_key = None
                handled.clear()
                active_key = None
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
                active_key = None
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
            if active_key:
                active_kind, active_start, active_end = active_key
                current_ranges = segments.get(active_kind, [])
                current = None
                for candidate in current_ranges:
                    if not isinstance(candidate, (tuple, list)) or len(candidate) != 2:
                        continue
                    candidate_key = (
                        round(float(tools.convert_time_to_seconds(candidate[0])), 3),
                        round(float(tools.convert_time_to_seconds(candidate[1])), 3),
                    )
                    if candidate_key == (active_start, active_end):
                        current = validate_range(candidate, duration)
                        break
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
                    handled.add(active_key)
                    _close(dialog)
                    active_key = None
                elif not current or now >= current[1] or not _enabled(active_kind):
                    handled.add(active_key)
                    _close(dialog)
                    active_key = None
                elif now < current[0] - 2:
                    # User sought backward; allow this same interval when they return.
                    _close(dialog)
                    active_key = None
                else:
                    continue
    
            modal_blocked = False
            for kind in ORDER:
                if not _enabled(kind):
                    continue
                ranges = segments.get(kind, [])
                if isinstance(ranges, (tuple, list)) and len(ranges) == 2 and not isinstance(ranges[0], (tuple, list)):
                    ranges = [ranges]
                for raw_bounds in ranges:
                    bounds = validate_range(raw_bounds, duration)
                    if not bounds:
                        continue
                    start, end = bounds
                    segment_key = (kind, round(start, 3), round(end, 3))
                    if segment_key in handled:
                        continue
                    if now >= end:
                        handled.add(segment_key)
                        continue
                    if not (start <= now < end):
                        continue
    
                    evidence = player.evidence_for(kind, bounds)
                    auto_allowed = can_auto_skip(_mode(kind), evidence.get('source'),
                                                 evidence.get('confidence'), evidence.get('submissions'))
                    # IntroDB does not confirm that a film lacks post-credit scenes.
                    # Without an identified post-credit interval, require a manual prompt.
                    if kind == 'movie_outro' and not player.post_credits:
                        auto_allowed = False
                    if auto_allowed:
                        try:
                            if end - 1.0 > now:
                                player.seekTime(max(0.0, end - 1.0))
                                player.reset_segment(kind, bounds)
                                handled.add(segment_key)
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
                        modal_blocked = True
                        break
                    try:
                        dialog.configure(kind, end, start)
                        dialog.show()
                        active_key = segment_key
                    except Exception as exc:
                        tools.log('Could not show {} prompt: {}'.format(kind, exc), 'warning')
                    break
                if active_key or modal_blocked:
                    break
    
    
    finally:
        player.shutdown()
