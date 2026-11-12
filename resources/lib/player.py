# -*- coding: utf-8 -*-
import xbmc
import threading
import os
import re
from urllib.parse import unquote, urlsplit
import xbmcvfs

from resources.lib import settings
from resources.lib import tools
from resources.lib.identifier import Identifier
from resources.lib.skip_dialog import IntroSkipDialog

_addon_path = xbmcvfs.translatePath(settings.get_addon_info('path'))


class Player(xbmc.Player):
    def __init__(self):
        super().__init__("Player")
        self.intro = None
        self.outro = None
        self.recap = None
        self.movie_outro = None
        self.post_credits = None
        self.segment_evidence = {}
        self.playback_generation = 0
        self._media_type = None
        self.identifier = Identifier()
        self._state_lock = threading.RLock()
        self._requested_keys = set()
        self._network_results = {}
        self._episode_key = None
        self._pending_notification = None
        self._active_title = ''
        self.dialog = IntroSkipDialog(
            "intro_skip_dialog.xml", _addon_path, "Default", "1080i", player=self
        )

    def reset_intro(self):
        self.intro = None

    def get_intro(self):
        return self.intro

    def get_outro(self):
        return self.outro

    def get_recap(self):
        return self.recap

    def get_dialog(self):
        return self.dialog

    def get_segments(self):
        return {"recap": self.recap, "intro": self.intro, "outro": self.outro,
                "movie_outro": self.movie_outro}

    def reset_segment(self, kind):
        if kind in ("intro", "recap", "outro", "movie_outro"):
            setattr(self, kind, None)

    def evidence_for(self, kind):
        return self.segment_evidence.get(kind, {})

    def onPlayBackStarted(self):
        tools.log("onPlayBackStarted", "debug")
        self.playback_generation += 1
        self._media_type = None
        self.reset_intro()
        self.outro = None
        self.recap = None
        self.movie_outro = None
        self.post_credits = None
        self.segment_evidence = {}
        self.identifier.segment_evidence.clear()
        from resources.lib.chapters import ChaptersAdapter
        self.identifier.chapter_adapter = ChaptersAdapter()
        try:
            self.dialog.close()
        except Exception:
            pass
        # Reset dialog state for new episode
        if hasattr(self.dialog, '_cancelled'):
            self.dialog._cancelled = False
        try:
            self.dialog.setProperty("cancelled", "False")
        except Exception:
            pass
        with self._state_lock:
            self._episode_key = None
            self._network_results.clear()
            self._requested_keys.clear()
            self._pending_notification = None
            self._active_title = ''

    @staticmethod
    def _filename_title(media_type, filename):
        """Last resort: read the name from a Seren/file URL, not Kodi's ID library."""
        try:
            name = os.path.basename(unquote(urlsplit(str(filename or '')).path))
        except (ValueError, TypeError):
            return ''
        if not name:
            return ''
        # A TV filename can give the show title and SxxExx even without tags.
        if media_type == 'episode':
            match = re.search(r'(?i)^(.*?)[. _-]+S\d{1,2}[. _-]*E\d{1,3}\b', name)
            stem = match.group(1) if match else ''
        else:
            stem = re.sub(r'(?i)\.(?:mkv|mp4|avi|mov|m4v)$', '', name)
            stem = re.split(r'(?i)[. _-]+(?:18\d{2}|19\d{2}|20\d{2})[. _-]+', stem, maxsplit=1)[0]
        return re.sub(r'[._]+', ' ', stem).strip(' -')

    def _media_title(self, tag, media_type):
        candidates = []
        try:
            candidates.append(tag.getTVShowTitle() if media_type == 'episode' else tag.getTitle())
        except Exception:
            pass
        if media_type == 'episode':
            candidates.extend([xbmc.getInfoLabel('VideoPlayer.TVShowTitle'),
                               xbmc.getInfoLabel('ListItem.TVShowTitle')])
        else:
            candidates.extend([xbmc.getInfoLabel('VideoPlayer.Title'),
                               xbmc.getInfoLabel('ListItem.Title')])
        # No Kodi library ID, JSON-RPC library search or manual user action.
        for title in candidates:
            if isinstance(title, str) and title.strip():
                return title.strip()
        try:
            return self._filename_title(media_type, self.getPlayingFile())
        except Exception:
            return ''

    @staticmethod
    def _media_year(tag, media_type):
        # Episode getYear() is typically the AIR date, not series debut.
        if media_type == 'episode':
            return None
        try:
            value = int(tag.getYear())
            return value if 1870 <= value <= 2100 else None
        except (TypeError, ValueError, RuntimeError, AttributeError):
            return None

    def chapters_ready(self):
        """Avoid repeat fetches after a complete list is available."""
        adapter = self.identifier.chapter_adapter
        return bool(adapter.chapter_cache)

    @staticmethod
    def _source_rank(source):
        return {'chapter_explicit': 30, 'introdb': 20,
                'chapter_heuristic': 10, 'chapter': 10}.get(source, 0)

    def _remember_segment(self, kind, bounds, evidence):
        """Keep the strongest result while logging source disagreements.

        Explicit source-local chapters beat community reference timings.
        Unnamed chapter guesses are Ask-only.
        """
        if not bounds:
            return False
        source = evidence.get('source', 'unknown')
        with self._state_lock:
            previous = getattr(self, kind, None)
            existing = self.segment_evidence.get(kind, {})
            prev_source = existing.get('source', '')
            if previous and previous != bounds and prev_source and prev_source != source:
                tools.log('Detector disagreement for {}: {}={} vs {}={}'.format(
                    kind, prev_source, previous, source, bounds), 'info')
            if previous and self._source_rank(prev_source) >= self._source_rank(source):
                return False
            setattr(self, kind, bounds)
            self.segment_evidence[kind] = dict(evidence)
            tools.log('Selected {} from {}: {}'.format(kind, source, bounds), 'info')
            if kind in ('movie_outro', 'post_credits'):
                self._protect_postcredits()
            return True

    def _protect_postcredits(self):
        if self.movie_outro and self.post_credits:
            from resources.lib.segment_policy import stop_before_postcredits
            self.movie_outro = stop_before_postcredits(self.movie_outro, self.post_credits)

    def take_detection_notification(self):
        with self._state_lock:
            msg = self._pending_notification
            self._pending_notification = None
        return msg

    def _launch_introdb(self, key, title='', year=None):
        """Resolve with Cinemeta, then fetch IntroDB in one background worker."""
        if not title:
            tools.log('No playing title available for Cinemeta; Kodi chapters still enabled', 'info')
            return
        with self._state_lock:
            if key in self._requested_keys:
                return
            self._requested_keys.add(key)
        threading.Thread(target=self._introdb_worker, args=(key,title,year),
                         name='IntroSkip-Cinemeta', daemon=True).start()

    def _introdb_worker(self, key, title='', year=None):
        """Network-only worker. Playback state is applied on the service thread."""
        gen, kind, _, season, episode = key
        try:
            from resources.lib.cinemeta import lookup_imdb
            imdb = lookup_imdb(title, kind, year)
        except Exception as exc:
            tools.log('Cinemeta resolver error: {}'.format(type(exc).__name__), 'warning')
            imdb = None
        if not imdb:
            tools.log('No verified Cinemeta ID for {!r}; using chapters only'.format(title), 'info')
            return
        with self._state_lock:
            if gen != self.playback_generation:
                return
        try:
            data = (self.identifier.introdb_adapter.get_movie_data(imdb)
                    if kind == 'movie' else
                    self.identifier.introdb_adapter.get_episode_data(imdb, season, episode))
        except Exception as exc:
            tools.log('IntroDB worker request failed: {}'.format(type(exc).__name__), 'warning')
            data = None
        with self._state_lock:
            if gen != self.playback_generation or key != self._episode_key:
                tools.log('Ignored stale Cinemeta/IntroDB playback result', 'debug')
                return
            self._network_results[key] = (imdb, data)

    def apply_ready_network_results(self):
        """Service-thread application; no xbmcgui/settings calls in HTTP workers."""
        with self._state_lock:
            key = self._episode_key
            ready = self._network_results.pop(key, None) if key else None
            if not ready:
                return False
            imdb, data = ready
            self._episode_key = (key[0], key[1], imdb, key[3], key[4])
            self._network_results.clear()
            if isinstance(data, dict):
                self._apply_introdb_data(key[1], data)
                return True
        return False

    def _apply_introdb_data(self, media_type, data):
        """Store provider evidence without replacing stronger local chapters."""
        if not isinstance(data, dict):
            return
        candidates = (('movie_outro', 'outro'), ('post_credits', 'post_credits')) if media_type == 'movie' else (
            ('intro', 'intro'), ('recap', 'recap'), ('outro', 'outro'))
        found = []
        for kind, key in candidates:
            if kind == 'intro' and not settings.get_setting_boolean('general.use_intro'):
                continue
            if kind == 'recap' and not settings.get_setting_boolean('general.use_recap'):
                continue
            if kind == 'outro' and not settings.get_setting_boolean('general.use_outro'):
                continue
            points = self.identifier.introdb_adapter.get_points_from_data(data, key)
            if not points:
                continue
            raw = data.get(key)
            if isinstance(raw, list):
                raw = raw[0] if raw else {}
            if not isinstance(raw, dict):
                raw = {}
            evidence = {'source': 'introdb', 'confidence': raw.get('confidence'),
                        'submissions': raw.get('submission_count')}
            if self._remember_segment(kind, points[0], evidence):
                found.append(kind)
        if found:
            self._pending_notification = 'IntroDB: ' + ', '.join(found)

    def _read_local_chapters(self, media_type, imdb_id, season, episode):
        kinds = ('movie_outro', 'post_credits') if media_type == 'movie' else ('intro', 'recap', 'outro')
        for kind in kinds:
            if kind == 'intro' and not settings.get_setting_boolean('general.use_intro'):
                continue
            if kind == 'recap' and not settings.get_setting_boolean('general.use_recap'):
                continue
            if kind == 'outro' and not settings.get_setting_boolean('general.use_outro'):
                continue
            try:
                points = self.identifier.chapter_adapter.get_points(imdb_id, season, episode, kind)
                if points:
                    self._remember_segment(kind, points[0], {
                        'source': self.identifier.chapter_adapter.last_match_kind or 'chapter'})
            except Exception as exc:
                tools.log('Kodi 22 {} chapter lookup failed: {}'.format(kind, exc), 'warning')

    def onAVStarted(self):
        """Run native chapters immediately; resolve IDs by Cinemeta concurrently."""
        tools.log('onAVStarted: Kodi chapters + keyless Cinemeta/IntroDB', 'info')
        gen = self.playback_generation
        try:
            video_meta = self.getVideoInfoTag()
            media_type = video_meta.getMediaType()
            self._media_type = media_type
        except Exception as exc:
            tools.log('Could not read playing video metadata: {}'.format(exc), 'warning')
            return
        if media_type not in ('episode', 'movie'):
            tools.log('Kodi playing item is neither episode nor movie', 'debug')
            return
        if media_type == 'episode' and not any(settings.get_setting_boolean(key) for key in (
                'general.use_intro', 'general.use_recap', 'general.use_outro')):
            tools.log('All TV segments disabled; skipping detection', 'info')
            self._media_type = None
            return
        if media_type == 'movie' and not settings.get_setting_boolean('general.use_movie_credits'):
            return
        if media_type == 'episode':
            try:
                season, episode = str(video_meta.getSeason()), str(video_meta.getEpisode())
            except Exception:
                season, episode = '0', '0'
        else:
            season, episode = '0', '0'
        key = (gen, media_type, '', season, episode)
        title = self._media_title(video_meta, media_type)
        year = self._media_year(video_meta, media_type)
        with self._state_lock:
            self._episode_key = key
            self._active_title = title
        tools.log('Playback metadata: {} title={!r} S{}E{}'.format(
            media_type, title, season, episode), 'info')
        self._launch_introdb(key, title=title, year=year)
        self._read_local_chapters(media_type, '', season, episode)
        self.apply_ready_network_results()
        with self._state_lock:
            if self.segment_evidence:
                self._pending_notification = 'Detected: ' + ', '.join(self.segment_evidence)
        tools.log('Kodi chapter pass complete; Cinemeta/IntroDB may finish independently', 'info')

    def refresh_chapter_segments(self, force=False):
        """Re-evaluate later chapter metadata; stronger labels can beat IntroDB."""
        if self._media_type not in ('episode', 'movie'):
            return False
        adapter = self.identifier.chapter_adapter
        chapters = adapter._get_chapters_multiple_methods(force=force)
        if not chapters:
            return False
        kinds = ('movie_outro', 'post_credits') if self._media_type == 'movie' else ('intro', 'recap', 'outro')
        updated = False
        for kind in kinds:
            if kind == 'intro' and not settings.get_setting_boolean('general.use_intro'):
                continue
            if kind == 'recap' and not settings.get_setting_boolean('general.use_recap'):
                continue
            if kind == 'outro' and not settings.get_setting_boolean('general.use_outro'):
                continue
            try:
                points = adapter.get_points('', 0, 0, kind)
                if points and self._remember_segment(kind, points[0], {
                    'source': adapter.last_match_kind or 'chapter'}):
                    tools.log('Delayed Kodi 22 chapter match for {}'.format(kind), 'info')
                    updated = True
            except Exception as exc:
                tools.log('Delayed {} chapter classification failed: {}'.format(kind, exc), 'warning')
        return updated

    def onPlayBackStopped(self):
        tools.log("onPlaybackStopped", "debug")
        try:
            self.dialog.close()
        except Exception:
            pass
        self.reset_intro()
        self.outro = None
        self.recap = None
        self.movie_outro = None
        self.post_credits = None
        self._media_type = None
        self._active_title = ''
        self.segment_evidence = {}
        self.playback_generation += 1
        with self._state_lock:
            self._episode_key = None
            self._network_results.clear()
            self._requested_keys.clear()
            self._pending_notification = None
