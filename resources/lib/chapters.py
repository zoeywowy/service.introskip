# -*- coding: utf-8 -*-
"""Kodi 22 native chapter extraction and conservative skip-segment matching.

Kodi 22's Player.GetChapters returns one-based index, optional name and start
position in SECONDS. Do not use Player.GetProperties(['chapters']) (unsupported)
or fabricated indexed InfoLabels. A source may not expose chapters at all.
"""
import math
import re

import xbmc

from resources.lib import tools
from resources.lib.adapter import PointsAdapter


CATEGORIES = ('intro', 'recap', 'outro', 'movie_outro', 'post_credits')
INTRO = ('intro', 'opening', 'main title', 'main titles', 'title sequence',
         'opening title', 'opening credits', 'opening theme', 'theme song',
         'opening sequence', 'ouverture', 'apertura', '开场', '오프닝')
RECAP = ('recap', 'previously on', 'previously in', 'last time on',
         'the story so far', 'previously', 'récapitulatif', '前情提要',
         'resumen anterior', 'rückblick')
CREDITS = ('end credits', 'closing credits', 'credits roll', 'credits',
           'end titles', 'final credits', 'closing titles', 'ending credits',
           'closing theme', 'end theme', 'outro', 'générique de fin')
POST = ('post-credit', 'post credit', 'after-credit', 'after credit',
        'mid-credit', 'mid credit', 'stinger', 'bonus scene')


def _generic(title):
    return not title or bool(re.match(r'^(chapter|chapitre|cap[ií]tulo|kapitel|scene|part)\s*[#0-9ivx\-]*$', title.strip().lower()))


def _matched(title, keywords):
    title = str(title or '').lower()
    return any(word in title for word in keywords)


class ChaptersAdapter(PointsAdapter):
    def __init__(self):
        self.player = xbmc.Player()
        self.chapter_cache = None
        self.last_status = 'not checked'
        self.last_count = 0
        self.last_generic_count = 0
        self.fetch_attempts = 0

    @staticmethod
    def _parse_time(value):
        if value is None or isinstance(value, bool):
            return None
        if isinstance(value, dict):
            try:
                v = (int(value.get('hours', 0))*3600 + int(value.get('minutes', 0))*60
                     + float(value.get('seconds', 0)) + float(value.get('milliseconds', 0))/1000.0)
            except (TypeError, ValueError, OverflowError):
                return None
        else:
            try:
                v = float(value)
            except (TypeError, ValueError, OverflowError):
                try:
                    parts = str(value).strip().split(':')
                    if len(parts) == 3:
                        v = int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
                    elif len(parts) == 2:
                        v = int(parts[0])*60 + float(parts[1])
                    else:
                        return None
                except (TypeError, ValueError, OverflowError):
                    return None
        return v if math.isfinite(v) and v >= 0 else None

    def _get_chapters_via_kodi22(self):
        try:
            players = tools.execute_jsonrpc('Player.GetActivePlayers')
            if not isinstance(players, list):
                self.last_status = 'active-player query unavailable'
                tools.log('Kodi chapter fetch: Player.GetActivePlayers did not return a list', 'warning')
                return []
            video = next((p for p in players if isinstance(p, dict) and p.get('type') == 'video'), None)
            if video is None:
                self.last_status = 'no active Kodi video player'
                tools.log('Kodi chapter fetch: Kodi reports no active video player', 'info')
                return []
            player_id = video.get('playerid')
            if not isinstance(player_id, int):
                self.last_status = 'video player ID missing'
                tools.log('Kodi chapter fetch: active video player is missing a valid ID', 'warning')
                return []
            self.fetch_attempts += 1
            attempt = self.fetch_attempts
            tools.log('Kodi chapter fetch #{}: calling Player.GetChapters(playerid={})'.format(
                attempt, player_id), 'info')
            result = tools.execute_jsonrpc('Player.GetChapters', {'playerid': player_id})
            if not isinstance(result, dict) or not isinstance(result.get('chapters'), list):
                self.last_status = 'Player.GetChapters unavailable or failed'
                tools.log('Kodi chapter fetch #{}: no chapter list in API response ({})'.format(
                    attempt, type(result).__name__), 'warning')
                return []
            raw = result['chapters']
            self.last_count = len(raw)
            tools.log('Kodi chapter fetch #{}: received {} chapter records'.format(
                attempt, len(raw)), 'info')
            if not raw:
                tools.log('Kodi chapter fetch #{}: stream exposes no chapters to Kodi'.format(
                    attempt), 'info')
            try:
                total = float(self.player.getTotalTime() or 0)
            except (ValueError, TypeError, RuntimeError, OverflowError):
                total = 0.0
            if not math.isfinite(total) or total < 0:
                total = 0.0
            entries = []
            for i, item in enumerate(raw, 1):
                if not isinstance(item, dict):
                    tools.log('Kodi chapter fetch #{}: record {}/{} rejected (not an object: {})'.format(
                        attempt, i, len(raw), type(item).__name__), 'info')
                    continue
                raw_name = str(item.get('name') or '').strip()
                raw_time = item.get('time')
                raw_index = item.get('index', i)
                start = self._parse_time(raw_time)
                if start is None or (total and start >= total):
                    continue
                # Kodi 22 uses the keys name/time/index; the time is an
                # absolute playback position in seconds.
                title = raw_name
                index = raw_index
                try:
                    index = int(index)
                except (ValueError, TypeError):
                    index = i
                entries.append({'number': index, 'title': title or 'Chapter {}'.format(index),
                                'start': start, 'start_label': '{:.2f}s'.format(start),
                                'source': 'kodi22', 'named': bool(title) and not _generic(title)})
            # Avoid zero/duplicate/invalid ranges and calculate end from the next chapter.
            entries.sort(key=lambda item: item['start'])
            chapters = []
            for chapter in entries:
                if chapters and chapter['start'] - chapters[-1]['start'] < 0.5:
                    if chapter['named'] and not chapters[-1]['named']:
                        chapters[-1] = chapter
                    continue
                chapters.append(chapter)
            for i, chapter in enumerate(chapters):
                chapter['end'] = (chapters[i+1]['start'] if i+1 < len(chapters) else total)
            self.last_generic_count = sum(not c['named'] for c in chapters)
            self.last_status = ('no chapter markers exposed by current stream' if not raw
                                else '{} chapters exposed ({} unnamed/generic)'.format(
                                    len(chapters), self.last_generic_count))
            tools.log('Kodi chapter fetch #{} complete: {} raw, {} valid distinct, {} unnamed/generic'.format(
                attempt, len(raw), len(chapters), self.last_generic_count), 'info')
            return chapters
        except Exception as exc:
            self.last_status = 'chapter query error'
            tools.log('Kodi 22 chapter query failed: {}'.format(exc), 'warning')
            return []

    def _get_chapters_multiple_methods(self, force=False):
        # Keep this method name because Identifier and previous integration tests
        # use it; the implementation is deliberately Kodi 22 native-only.
        if self.chapter_cache is not None and not force:
            return self.chapter_cache
        chapters = self._get_chapters_via_kodi22()
        if chapters:
            self.chapter_cache = chapters
            tools.log('Kodi 22: {}'.format(self.last_status), 'info')
        else:
            # Empty results are deliberately not cached; some streams only
            # publish chapter information seconds after AV playback starts.
            self.chapter_cache = None
            tools.log('Kodi 22 chapter check: {}'.format(self.last_status), 'info')
        return chapters

    @staticmethod
    def _find_explicit_segment_chapter(chapters, segment_type):
        for c in chapters:
            title = str(c.get('title') or '').strip()
            if _generic(title):
                continue
            if segment_type == 'intro':
                if _matched(title, INTRO) and not _matched(title, RECAP + POST):
                    return c
            elif segment_type == 'recap':
                if _matched(title, RECAP):
                    return c
            elif segment_type == 'post_credits':
                if _matched(title, POST):
                    return c
            elif segment_type in ('outro', 'movie_outro'):
                # Do not incorrectly treat a mid/post-credit scene as credits.
                if _matched(title, CREDITS) and not _matched(title, POST + INTRO):
                    return c
        return None

    def _find_intro_chapter(self, chapters):
        explicit = self._find_explicit_segment_chapter(chapters, 'intro')
        if explicit:
            return explicit, 'chapter_explicit'
        # Unnamed chapters are *not* evidence of an intro, but an appropriately
        # early bounded one can be offered for manual confirmation only.
        try:
            duration = float(self.player.getTotalTime() or 0)
        except (ValueError, TypeError, RuntimeError, OverflowError):
            duration = 0.0
        if duration <= 0 or not math.isfinite(duration):
            return None, None
        candidates = [c for c in chapters if
                      10 <= c['start'] < min(duration * .2, 900)
                      and 25 <= c['end']-c['start'] <= 150
                      and not _matched(c['title'], RECAP+POST+CREDITS)]
        if len(candidates) == 1:
            return candidates[0], 'chapter_heuristic'
        return None, None

    def get_points(self, imdb, season, episode, type=None):
        if type not in CATEGORIES:
            return None
        chapters = self._get_chapters_multiple_methods()
        if not chapters:
            return None
        if type == 'intro':
            chapter, method = self._find_intro_chapter(chapters)
        else:
            chapter = self._find_explicit_segment_chapter(chapters, type)
            method = 'chapter_explicit' if chapter else None
        if chapter is None:
            tools.log('Kodi returned chapters but no trusted {} marker'.format(type), 'info')
            return None
        try:
            total = float(self.player.getTotalTime() or 0)
        except (ValueError, TypeError, RuntimeError, OverflowError):
            total = 0.0
        start = float(chapter['start'])
        end = float(chapter['end'])
        if type == 'intro' and method == 'chapter_explicit':
            # A title sequence immediately following opening credits is part of
            # the same intro. Never merge generic scene, recap or credit labels.
            try:
                pos = next(i for i, entry in enumerate(chapters)
                           if abs(entry['start']-start) < .25)
                for following in chapters[pos+1:]:
                    if abs(float(following['start']) - end) > 1.0:
                        break
                    label = following.get('title', '')
                    if (_generic(label) or not _matched(label, INTRO)
                            or _matched(label, RECAP+CREDITS+POST)):
                        break
                    new_end = float(following['end'])
                    if new_end-start > 360 or new_end <= end:
                        break
                    tools.log('Merged adjacent named intro chapter: {}'.format(label), 'info')
                    end = new_end
            except (StopIteration, TypeError, ValueError):
                pass
        if not math.isfinite(end) or end <= start or (total and start >= total):
            return None
        if total > 0:
            end = min(end, total)
        if type == 'intro' and end - start > 360:
            tools.log('Ignoring implausibly long intro chapter span', 'info')
            return None
        if type == 'recap' and (end-start > 480 or (total > 0 and start > total*.33)):
            return None
        if type in ('outro', 'movie_outro', 'post_credits') and total > 0 and start < total*.55:
            return None
        self.last_match_kind = method
        tools.log('Kodi chapter {} matched {}: {} ({:.1f}-{:.1f}s)'.format(
            chapter['number'], type, chapter['title'], start, end), 'info')
        return [(start, end)]
