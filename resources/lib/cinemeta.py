# -*- coding: utf-8 -*-
"""Keyless, per-playback IMDb ID search against Stremio's public Cinemeta.

No Kodi library scraping, OMDb credentials, or on-disk metadata cache.
Safely refuse ambiguous titles rather than using Cinemeta's search ranking.
"""
import html
import re
import unicodedata
from urllib.parse import quote

import requests

from resources.lib import tools

BASE_URL = 'https://v3-cinemeta.strem.io'
IMDB = re.compile(r'tt\d{7,10}\Z', flags=re.I)
YEAR = re.compile(r'^\s*(18\d{2}|19\d{2}|20\d{2}|2100)(?!\d)')


def _normalize(value):
    """Normalize accents and punctuation; keep letters and digits together."""
    value = html.unescape(str(value or '')).casefold()
    value = unicodedata.normalize('NFKD', value)
    value = ''.join(c for c in value if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '', value)


def _no_article(value):
    value = re.sub(r'[^a-z0-9]+', ' ', html.unescape(str(value or '')).casefold()).strip()
    return re.sub(r'^(the|a|an)\s+', '', value)


def _year(value):
    match = YEAR.match(str(value or ''))
    return int(match.group(1)) if match else None


def _candidate_year(candidate):
    for k in ('releaseInfo', 'year', 'released'):
        value = _year(candidate.get(k))
        if value:
            return value
    return None


def _match_rank(query_title, candidate_title):
    """Exact match, or unambiguous subtitle separated by punctuation.

    'The Rings of Power' can match 'The Lord of the Rings: The Rings of Power',
    but NOT 'She-Ra and the Princesses of Power'.
    """
    if _normalize(query_title) == _normalize(candidate_title):
        return 3
    # An omitted 'the' should not change an otherwise exact show title.
    if _normalize(_no_article(query_title)) == _normalize(_no_article(candidate_title)):
        return 2
    # The shortened series name may be used by a playback provider.
    for part in re.split(r'\s*[:：]\s*|\s+[—–]\s+', str(candidate_title or ''))[1:]:
        if _normalize(part) == _normalize(query_title) or _normalize(_no_article(part)) == _normalize(_no_article(query_title)):
            return 1
    return 0


def _verified_candidates(payload, title, kind, year=None):
    """Return best verified IMDb ID, or None if missing/ambiguous."""
    if not isinstance(payload, dict) or not isinstance(payload.get('metas'), list):
        return None
    wanted_year = _year(year)
    matches = {}
    for item in payload['metas']:
        if not isinstance(item, dict) or item.get('type') != kind:
            continue
        imdb = str(item.get('id') or item.get('imdb_id') or '').strip()
        if not IMDB.fullmatch(imdb):
            continue
        # If both identifiers exist they must refer to the same title.
        other = item.get('imdb_id')
        if other is not None and str(other).strip().lower() != imdb.lower():
            continue
        rank = _match_rank(title, item.get('name'))
        if not rank:
            continue
        candidate_year = _candidate_year(item)
        if wanted_year is not None and candidate_year != wanted_year:
            continue
        imdb = imdb.lower()
        matches[imdb] = max(rank, matches.get(imdb, 0))
    if not matches:
        return None
    highest = max(matches.values())
    winners = [imdb for imdb, rank in matches.items() if rank == highest]
    return winners[0] if len(winners) == 1 else None


def lookup_imdb(title, media_type, year=None, timeout=5):
    """Search a series or film title, return a verified IMDb ID or None.

    TV lookup is *series-level*; the caller supplies season/episode to IntroDB.
    Never persist IDs or timestamp data. One outbound GET per invocation.
    """
    title = str(title or '').strip()
    kind = 'series' if media_type in ('episode', 'series') else 'movie' if media_type == 'movie' else None
    if not kind or len(_normalize(title)) < 3 or len(title) > 200:
        return None
    url = '{}/catalog/{}/top/search={}.json'.format(BASE_URL, kind, quote(title, safe=''))
    try:
        tools.log('Cinemeta searching {} title {!r}'.format(kind, title), 'info')
        response = requests.get(url, timeout=timeout, headers={'Accept': 'application/json'})
        response.raise_for_status()
        payload = response.json()
    except (requests.exceptions.RequestException, ValueError, TypeError) as exc:
        tools.log('Cinemeta lookup failed ({})'.format(type(exc).__name__), 'warning')
        return None
    imdb = _verified_candidates(payload, title, kind, year)
    if imdb:
        tools.log('Cinemeta verified {} IMDb ID: {}'.format(kind, imdb), 'info')
    else:
        tools.log('Cinemeta returned no unique verified {} match'.format(kind), 'info')
    return imdb
