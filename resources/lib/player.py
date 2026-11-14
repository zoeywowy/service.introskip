# -*- coding: utf-8 -*-
import xbmc
import threading
import time
import os
import re
from urllib.parse import unquote, urlsplit
import xbmcvfs

from resources.lib import settings
from resources.lib import tools
from resources.lib.identifier import Identifier

_addon_path = xbmcvfs.translatePath(settings.get_addon_info('path'))


class Player(xbmc.Player):
    def __init__(self):
        super().__init__()
        self.intro = None
        self.outro = None
        self.recap = None
        self.movie_outro = None
        self.post_credits = None
        self.preview = None
        self.segment_evidence = {}
        self._segment_ranges = {}
        self._segment_range_evidence = {}
        self.playback_generation = 0
        self._media_type = None
        self.identifier = Identifier()
        self._state_lock = threading.RLock()
        self._shutdown_event = threading.Event()
        self._workers = set()
        self._requested_keys = set()
        self._network_results = {}
        self._episode_key = None
        self._pending_notification = None
        self._active_title = ''
        # Native Kodi GUI windows must not exist while the service is idle.
        # Create the skip prompt only when playback actually needs it.
        self.dialog = None

    def get_dialog(self, create=False):
        """Only instantiate a native WindowXMLDialog when a prompt is needed."""
        if self.dialog is None and create and not self._shutdown_event.is_set():
            from resources.lib.skip_dialog import IntroSkipDialog
            self.dialog = IntroSkipDialog(
                "intro_skip_dialog.xml", _addon_path, "Default", "1080i", player=self
            )
        return self.dialog

    def get_segments(self):
        """Return a thread-safe snapshot of every currently selected interval."""
        with self._state_lock:
            result = {}
            for kind in ("recap", "intro", "preview", "outro", "movie_outro"):
                ranges = self._segment_ranges.get(kind)
                if not ranges:
                    current = getattr(self, kind, None)
                    ranges = [current] if current else []
                result[kind] = list(ranges)
            return result

    @staticmethod
    def _range_key(bounds):
        try:
            start = round(float(tools.convert_time_to_seconds(bounds[0])), 3)
            end = round(float(tools.convert_time_to_seconds(bounds[1])), 3)
            return (start, end)
        except (TypeError, ValueError, IndexError, OverflowError):
            return None

    def reset_segment(self, kind, bounds=None):
        """Remove one handled interval, or clear all intervals of a type."""
        if kind not in ("intro", "recap", "preview", "outro", "movie_outro", "post_credits"):
            return
        with self._state_lock:
            if bounds is None:
                self._segment_ranges.pop(kind, None)
                self._segment_range_evidence.pop(kind, None)
                self.segment_evidence.pop(kind, None)
                setattr(self, kind, None)
                return

            key = self._range_key(bounds)
            ranges = self._segment_ranges.get(kind, [])
            remaining = [item for item in ranges if self._range_key(item) != key]
            self._segment_ranges[kind] = remaining
            evidence = self._segment_range_evidence.get(kind, {})
            if key is not None:
                evidence.pop(key, None)
            if remaining:
                setattr(self, kind, remaining[0])
                first_key = self._range_key(remaining[0])
                self.segment_evidence[kind] = evidence.get(
                    first_key, self.segment_evidence.get(kind, {})
                )
            else:
                setattr(self, kind, None)
                self.segment_evidence.pop(kind, None)

    def evidence_for(self, kind, bounds=None):
        with self._state_lock:
            if bounds is not None:
                key = self._range_key(bounds)
                return self._segment_range_evidence.get(kind, {}).get(
                    key, self.segment_evidence.get(kind, {})
                )
            return self.segment_evidence.get(kind, {})

    def onPlayBackStarted(self):
        tools.log("onPlayBackStarted", "debug")
        from resources.lib.chapters import ChaptersAdapter

        with self._state_lock:
            self.playback_generation += 1
            self._media_type = None
            self.intro = None
            self.outro = None
            self.recap = None
            self.movie_outro = None
            self.post_credits = None
            self.preview = None
            self.segment_evidence = {}
            self._segment_ranges = {}
            self._segment_range_evidence = {}
            self.identifier.chapter_adapter = ChaptersAdapter()
            self._episode_key = None
            self._network_results.clear()
            self._requested_keys.clear()
            self._pending_notification = None
            self._active_title = ''

        dialog = self.dialog
        if dialog is not None:
            try:
                dialog.close()
            except Exception:
                pass
            # Do not allocate a new native window when playback changes.
            if hasattr(dialog, '_cancelled'):
                dialog._cancelled = False
            try:
                dialog.setProperty("cancelled", "False")
            except Exception:
                pass

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
        return {'chapter_explicit': 30, 'introdb': 20, 'theintrodb': 20,
                'chapter_heuristic': 10, 'chapter': 10}.get(source, 0)

    @staticmethod
    def _evidence_quality(evidence):
        evidence = evidence or {}
        try:
            confidence = float(evidence.get('confidence') or 0)
        except (TypeError, ValueError, OverflowError):
            confidence = 0
        try:
            submissions = int(evidence.get('submissions') or 0)
        except (TypeError, ValueError, OverflowError):
            submissions = 0
        return (1 if evidence.get('version_match') else 0, confidence, submissions)

    def _remember_segment(self, kind, bounds, evidence):
        """Backward-compatible single-range writer used by Kodi chapter detection."""
        return self._remember_segment_ranges(kind, [bounds] if bounds else [], evidence)

    def _remember_segment_ranges(self, kind, ranges, evidence):
        """Keep every interval from the strongest provider for this segment type.

        Explicit source-local Kodi chapters outrank community data. Among
        community providers, duration match, confidence and submission count
        determine which provider group wins. All intervals from that winning
        group are retained for the playback service.
        """
        if kind not in ("intro", "recap", "preview", "outro", "movie_outro", "post_credits"):
            return False
        normalized = []
        for bounds in ranges or []:
            key = self._range_key(bounds)
            if key and key[0] >= 0 and key[1] > key[0]:
                normalized.append((key[0], key[1]))
        unique = {self._range_key(item): item for item in normalized}
        normalized = [unique[key] for key in sorted(unique)]
        if not normalized:
            return False

        source = (evidence or {}).get('source', 'unknown')
        with self._state_lock:
            previous = self._segment_ranges.get(kind, [])
            existing = self.segment_evidence.get(kind, {})
            prev_source = existing.get('source', '')
            if previous and previous != normalized and prev_source and prev_source != source:
                tools.log('Detector disagreement for {}: {}={} vs {}={}'.format(
                    kind, prev_source, previous, source, normalized), 'info')
            prev_rank = self._source_rank(prev_source)
            new_rank = self._source_rank(source)
            if previous and prev_rank > new_rank:
                return False
            if previous and prev_rank == new_rank:
                if self._evidence_quality(existing) >= self._evidence_quality(evidence):
                    return False

            self._segment_ranges[kind] = normalized
            evidence = dict(evidence or {})
            self._segment_range_evidence[kind] = {
                self._range_key(bounds): dict(evidence) for bounds in normalized
            }
            self.segment_evidence[kind] = dict(evidence)
            setattr(self, kind, normalized[0])
            tools.log('Selected {} from {}: {}'.format(kind, source, normalized), 'info')
            if kind in ('movie_outro', 'post_credits'):
                self._protect_postcredits()
            return True

    def _protect_postcredits(self):
        post_ranges = self._segment_ranges.get('post_credits', [])
        post = post_ranges[0] if post_ranges else self.post_credits
        credits = self._segment_ranges.get('movie_outro', [])
        if not credits and self.movie_outro:
            credits = [self.movie_outro]
        if not post or not credits:
            return
        from resources.lib.segment_policy import stop_before_postcredits
        protected = []
        for bounds in credits:
            clipped = stop_before_postcredits(bounds, post)
            if clipped:
                protected.append(clipped)
        self._segment_ranges['movie_outro'] = protected
        self.movie_outro = protected[0] if protected else None

    def take_detection_notification(self):
        with self._state_lock:
            msg = self._pending_notification
            self._pending_notification = None
        return msg

    def _launch_introdb(self, key, title='', year=None, duration_ms=0):
        """Launch at most one lookup per playback key, without delaying Kodi."""
        if self._shutdown_event.is_set() or not title:
            return
        with self._state_lock:
            if self._shutdown_event.is_set() or key in self._requested_keys:
                return
            self._requested_keys.add(key)
            worker = threading.Thread(
                target=self._run_introdb_worker,
                args=(key, title, year, duration_ms),
                name='IntroSkip-MultiSource',
                daemon=True,
            )
            self._workers.add(worker)
            try:
                worker.start()
            except Exception:
                self._workers.discard(worker)
                self._requested_keys.discard(key)
                raise

    def _run_introdb_worker(self, key, title, year, duration_ms):
        try:
            self._introdb_worker(key, title, year, duration_ms)
        finally:
            with self._state_lock:
                self._workers.discard(threading.current_thread())

    def _introdb_worker(self, key, title='', year=None, duration_ms=0):
        """Fetch the local IntroDB index and TheIntroDB v4 without blocking playback."""
        gen, kind, _, season, episode = key
        try:
            from resources.lib.cinemeta import lookup_imdb
            imdb = lookup_imdb(title, kind, year)
        except Exception as exc:
            tools.log('Cinemeta resolver error: {}'.format(type(exc).__name__), 'warning')
            imdb = None
        if not imdb:
            tools.log('No verified Cinemeta ID for {!r}; using Kodi chapters only'.format(title), 'info')
            return
        if self._shutdown_event.is_set():
            return
        with self._state_lock:
            if gen != self.playback_generation:
                return

        try:
            duration_ms = int(duration_ms or 0)
        except (TypeError, ValueError, OverflowError):
            duration_ms = 0
        providers = []

        # The daily open-data snapshot is the primary IntroDB source. It is
        # indexed locally and never causes a per-episode download.
        try:
            bulk_data = self.identifier.introdb_open_data.get_episode_data(
                imdb, season, episode, is_movie=(kind == 'movie')
            )
        except Exception as exc:
            tools.log('Local IntroDB lookup failed: {}'.format(type(exc).__name__), 'warning')
            bulk_data = None
        if self._shutdown_event.is_set():
            return
        if bulk_data is not None:
            providers.append(('introdb', bulk_data, 'open-data'))
        else:
            # If the snapshot is not installed yet or has no record, retain the
            # original one-episode IntroDB API as an online fallback.
            try:
                live_data = (
                    self.identifier.introdb_adapter.get_movie_data(imdb)
                    if kind == 'movie' else
                    self.identifier.introdb_adapter.get_episode_data(imdb, season, episode)
                )
            except Exception as exc:
                tools.log('IntroDB API fallback failed: {}'.format(type(exc).__name__), 'warning')
                live_data = None
            if self._shutdown_event.is_set():
                return
            if isinstance(live_data, dict):
                providers.append(('introdb', live_data, 'api'))

        if self._shutdown_event.is_set():
            return
        # TheIntroDB is an independent community source. IMDb is supported as
        # a fallback identity; duration_ms helps select the closest release cut.
        try:
            theintrodb_data = self.identifier.theintrodb_adapter.get_media_data(
                imdb, season, episode, is_movie=(kind == 'movie'), duration_ms=duration_ms
            )
        except Exception as exc:
            tools.log('TheIntroDB worker request failed: {}'.format(type(exc).__name__), 'warning')
            theintrodb_data = None
        if self._shutdown_event.is_set():
            return
        if isinstance(theintrodb_data, dict):
            providers.append(('theintrodb', theintrodb_data, 'v4'))

        with self._state_lock:
            if gen != self.playback_generation or key != self._episode_key:
                tools.log('Ignored stale multi-source playback result', 'debug')
                return
            self._network_results[key] = (imdb, providers, duration_ms)

    def apply_ready_network_results(self):
        """Apply worker results on the service thread, atomically with playback state."""
        with self._state_lock:
            key = self._episode_key
            ready = self._network_results.pop(key, None) if key else None
            if not ready:
                return False
            if key[0] != self.playback_generation:
                return False

            imdb, providers, duration_ms = ready
            self._episode_key = (key[0], key[1], imdb, key[3], key[4])
            self._network_results.clear()

            found = []
            duration_seconds = duration_ms / 1000.0 if duration_ms else 0.0
            for source, data, provider in providers:
                if source == 'introdb':
                    found.extend(self._apply_introdb_data(key[1], data, provider=provider))
                elif source == 'theintrodb':
                    found.extend(self._apply_theintrodb_data(
                        key[1], data, duration_ms, duration_seconds
                    ))

            if found:
                self._pending_notification = 'Community data: ' + ', '.join(sorted(set(found)))
            return bool(providers)

    def _apply_introdb_data(self, media_type, data, provider='api'):
        """Apply every IntroDB interval while retaining chapter precedence."""
        if not isinstance(data, dict):
            return []
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
            points = self.identifier.introdb_adapter.get_all_points_from_data(data, key)
            if not points:
                continue
            raw = data.get(key)
            raw_items = raw if isinstance(raw, list) else [raw]
            raw_items = [item for item in raw_items if isinstance(item, dict)]
            confidence_values = [
                item.get('confidence') for item in raw_items
                if isinstance(item.get('confidence'), (int, float)) and not isinstance(item.get('confidence'), bool)
            ]
            submission_values = [
                item.get('submission_count') for item in raw_items
                if isinstance(item.get('submission_count'), int) and not isinstance(item.get('submission_count'), bool)
            ]
            evidence = {
                'source': 'introdb',
                'provider': provider,
                'confidence': max(confidence_values) if confidence_values else None,
                'submissions': max(submission_values) if submission_values else 0,
            }
            if self._remember_segment_ranges(kind, points, evidence):
                found.append(kind)
        return found

    def _apply_theintrodb_data(self, media_type, data, duration_ms=0, duration_seconds=0):
        """Apply every duration-matched TheIntroDB v4 range, including previews."""
        if not isinstance(data, dict):
            return []
        if media_type == 'movie':
            candidates = (('movie_outro', 'credits'), ('preview', 'preview'))
        else:
            candidates = (('intro', 'intro'), ('recap', 'recap'),
                          ('outro', 'credits'), ('preview', 'preview'))
        found = []
        for kind, api_key in candidates:
            enabled_key = {
                'intro': 'general.use_intro',
                'recap': 'general.use_recap',
                'outro': 'general.use_outro',
                'movie_outro': 'general.use_movie_credits',
                'preview': 'general.use_preview',
            }[kind]
            if not settings.get_setting_boolean(enabled_key):
                continue
            ranges = self.identifier.theintrodb_adapter.get_ranges_from_data(
                data, api_key, duration_seconds
            )
            if not ranges:
                continue
            evidence = self.identifier.theintrodb_adapter.evidence_for(data, api_key, duration_ms)
            if self._remember_segment_ranges(kind, ranges, evidence):
                found.append(kind)
        return found

    def _read_local_chapters(self, media_type, imdb_id, season, episode):
        kinds = ('movie_outro', 'post_credits', 'preview') if media_type == 'movie' else ('intro', 'recap', 'outro', 'preview')
        for kind in kinds:
            if kind == 'intro' and not settings.get_setting_boolean('general.use_intro'):
                continue
            if kind == 'recap' and not settings.get_setting_boolean('general.use_recap'):
                continue
            if kind == 'outro' and not settings.get_setting_boolean('general.use_outro'):
                continue
            if kind == 'preview' and not settings.get_setting_boolean('general.use_preview'):
                continue
            try:
                points = self.identifier.chapter_adapter.get_points(imdb_id, season, episode, kind)
                if points:
                    self._remember_segment_ranges(kind, points, {
                        'source': self.identifier.chapter_adapter.last_match_kind or 'chapter'})
            except Exception as exc:
                tools.log('Kodi 22 {} chapter lookup failed: {}'.format(kind, exc), 'warning')

    def onAVStarted(self):
        """Run native chapters immediately; resolve IDs by Cinemeta concurrently."""
        if self._shutdown_event.is_set():
            return
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
                'general.use_intro', 'general.use_recap', 'general.use_outro', 'general.use_preview')):
            tools.log('All TV segments disabled; skipping detection', 'info')
            self._media_type = None
            return
        if media_type == 'movie' and not (
                settings.get_setting_boolean('general.use_movie_credits')
                or settings.get_setting_boolean('general.use_preview')):
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
        try:
            duration_ms = int(float(self.getTotalTime() or 0) * 1000)
        except (TypeError, ValueError, RuntimeError, OverflowError):
            duration_ms = 0
        self._launch_introdb(key, title=title, year=year, duration_ms=duration_ms)
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
        kinds = ('movie_outro', 'post_credits', 'preview') if self._media_type == 'movie' else ('intro', 'recap', 'outro', 'preview')
        updated = False
        for kind in kinds:
            if kind == 'intro' and not settings.get_setting_boolean('general.use_intro'):
                continue
            if kind == 'recap' and not settings.get_setting_boolean('general.use_recap'):
                continue
            if kind == 'outro' and not settings.get_setting_boolean('general.use_outro'):
                continue
            if kind == 'preview' and not settings.get_setting_boolean('general.use_preview'):
                continue
            try:
                points = adapter.get_points('', 0, 0, kind)
                if points and self._remember_segment_ranges(kind, points, {
                    'source': adapter.last_match_kind or 'chapter'}):
                    tools.log('Delayed Kodi 22 chapter match for {}'.format(kind), 'info')
                    updated = True
            except Exception as exc:
                tools.log('Delayed {} chapter classification failed: {}'.format(kind, exc), 'warning')
        return updated

    def shutdown(self):
        """Stop background work with one bounded deadline before Kodi unloads us."""
        self._shutdown_event.set()
        tools.log('Shutdown: cancellation requested', 'info')
        sync_worker = None
        try:
            sync_worker = self.identifier.cancel_background_work()
        except Exception as exc:
            tools.log('Shutdown: sync cancellation error ({})'.format(type(exc).__name__), 'warning')
        with self._state_lock:
            self._network_results.clear()
            self._requested_keys.clear()
            self._pending_notification = None
            workers = list(self._workers)
        # Kodi can wait for daemon thread states too. Leave spare time below
        # Kodi's five-second Python shutdown limit for native cleanup.
        if sync_worker is not None:
            workers.insert(0, sync_worker)
        deadline = time.monotonic() + 3.25
        for worker in workers:
            if worker is threading.current_thread():
                continue
            try:
                if not worker.is_alive():
                    continue
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    tools.log('Shutdown: worker budget exhausted', 'warning')
                    break
                worker.join(timeout=remaining)
                if worker.is_alive():
                    tools.log('Shutdown: {} still running'.format(worker.name), 'warning')
                else:
                    tools.log('Shutdown: {} stopped'.format(worker.name), 'debug')
            except RuntimeError as exc:
                tools.log('Shutdown: worker join error ({})'.format(exc), 'warning')

        dialog = self.dialog
        self.dialog = None
        if dialog is not None:
            try:
                dialog.close()
            except Exception as exc:
                tools.log('Shutdown: dialog close error ({})'.format(exc), 'warning')
            dialog.player = None
        tools.log('Shutdown: UI resources released', 'info')

    def onPlayBackStopped(self):
        tools.log("onPlaybackStopped", "debug")
        if self.dialog is not None:
            try:
                self.dialog.close()
            except Exception:
                pass

        with self._state_lock:
            self.intro = None
            self.outro = None
            self.recap = None
            self.movie_outro = None
            self.post_credits = None
            self.preview = None
            self._segment_ranges = {}
            self._segment_range_evidence = {}
            self._media_type = None
            self._active_title = ''
            self.segment_evidence = {}
            self.playback_generation += 1
            self._episode_key = None
            self._network_results.clear()
            self._requested_keys.clear()
            self._pending_notification = None

