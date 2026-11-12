# How IntroSkip finds something to skip

IntroSkip combines two independent sources: community timing data from **IntroDB** and chapter markers exposed by **Kodi 22**.

## 1. Identify the playing title

Kodi provides the title and media type from the currently playing item, plus season and episode numbers for TV. If necessary, IntroSkip may try to work out a title from the filename.

For IntroDB lookups, IntroSkip searches **Cinemeta** for the matching movie or TV series. It checks the title, type and movie year when available, and avoids choosing an uncertain match. Cinemeta supplies an IMDb ID; IntroDB uses that ID (and season/episode for TV) to find community-submitted skip times.

Cinemeta does **not** need an account, Stremio installation or API key. IntroSkip no longer queries OMDb or Kodi library scrapers to resolve IMDb IDs.

## 2. Check Kodi chapters

Independently of the online lookup, IntroSkip reads chapter data from Kodi 22 when the player provides it. Clear chapter names such as opening credits, recaps or end credits may give local skip boundaries. Adjacent named opening chapters may be combined where appropriate.

These are not guaranteed to exist: chapters depend on the actual video, container and player.

## 3. Decide whether to show a button

If the segment type is enabled and a valid boundary is found, IntroSkip can display a skip button. Explicit local chapter boundaries take priority when they disagree with online timestamps for a different cut.

The default is **Ask**. **Auto** requires qualifying IntroDB evidence and additional safety checks. It does not blindly skip unnamed chapters or unverified guesses. Movie credits are especially conservative about post-credit material.

## What IntroSkip does not do

It does not read or download subtitles, use subtitle phrase detection, require an OMDb/TVDB API key, or maintain a persistent database of IMDb IDs or skip timestamps. Only the current playback session's results are kept in memory.

If a provider does not expose enough information, it is normal for IntroSkip to show no button. See [Troubleshooting](TROUBLESHOOTING.md).
