# Detection and identifiers

## Media identification

On playback, IntroSkip reads the available title and media type from the playing item. For episodes it also needs season/episode. If title metadata is absent, the filename may be parsed as a last resort. It does **not** ask Kodi's library scraper for an IMDb ID.

IntroSkip searches the public [Cinemeta](https://v3-cinemeta.strem.io/manifest.json) title catalog (`series` for episodes, `movie` for films). It validates media type, title, and movie release year when provided, then uses a unique candidate's IMDb ID to request timestamps from IntroDB. Cinemeta can be unreachable or yield multiple titles, in which case no ID is guessed. **No API key** is required.

## Native chapters

Kodi 22 `Player.GetChapters` is checked independently of Cinemeta/IntroDB. Named chapter labels can supply skip boundaries for intro/recap/end credits. Adjacent explicitly named intro chapters may be joined. Chapters are source-local, so explicit matches outrank remote timestamp disagreements.

## Segment choice and safety

IntroSkip chooses between chapter evidence and IntroDB evidence according to source priority. The default is to **ask**. Automatic skips require suitable IntroDB evidence and opt-in per segment. Untitled/heuristic chapters must not trigger an unconfirmed automatic skip. Movies can have post-credit scenes, so credit skipping must respect those boundaries.

## Performance and privacy

Requests are handled away from the playback callback and results are accepted only for the same current playback session. No across-episode timestamp cache, stored IMDb-ID cache, subtitle processing or subtitle downloads. Logs can describe lookup outcomes.
