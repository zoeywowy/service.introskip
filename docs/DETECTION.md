# How IntroSkip finds something to skip

IntroSkip combines three independent foundations: the community-published **IntroDB** dataset and API, the second community source **TheIntroDB v4**, and chapter markers exposed by **Kodi 22**.

## 1. Identify the playing title

Kodi provides the title and media type from the currently playing item, plus season and episode numbers for TV. If necessary, IntroSkip may work out a title from the filename.

IntroSkip searches **Cinemeta** for a matching movie or TV series. It checks title, media type and movie year when available, and refuses uncertain matches. Cinemeta supplies an IMDb ID. IntroSkip does not query OMDb or perform Kodi library ID lookups.

## 2. IntroDB: local full-database lookup

IntroDB publishes a daily open-data snapshot:

- `manifest.json` identifies the snapshot and the compressed data files.
- `segments.csv.gz` contains all live episode/movie timestamp rows, including segment type, boundaries, confidence and submission count.
- `segmentless.csv.gz` records episodes the community has confirmed do not contain an intro, recap or outro.

At Kodi startup, IntroSkip checks the small manifest in a background thread. It downloads and verifies the compressed CSV files only when the manifest changes, then builds an indexed SQLite database under the add-on profile. The existing local database remains usable if the network is unavailable or a download fails.

When a title is playing, IntroSkip looks up its IMDb ID and episode coordinates locally. The single-episode IntroDB API remains a fallback if the local snapshot is not yet available or has no record for that item.

Contains data from IntroDB (introdb.app), available under the ODbL.

## 3. TheIntroDB v4: independent live source

IntroSkip also queries `https://api.theintrodb.org/v4/media` using the verified IMDb ID, season/episode when applicable, and the actual playback duration. The v4 API prefers TVDB identity, but it supports IMDb IDs as a slower fallback; IntroSkip does not introduce a Kodi library-ID lookup to obtain TVDB IDs.

Duration matching helps the API choose the closest release version, such as a theatrical or extended cut. The adapter preserves every valid interval returned for intros, recaps and credits, and can expose optional **Skip Preview** prompts. API responses are cached locally for seven days to avoid repeatedly requesting the same media.

The API is an additional source, not a dependency: a timeout, rate limit, missing record or malformed response must never stop IntroDB or Kodi chapter detection.

## 4. Kodi 22 native chapters

Independently of both online sources, IntroSkip reads chapter data from Kodi 22 when the player provides it. Clear chapter names such as opening credits, recaps or end credits may provide local skip boundaries. Adjacent named opening chapters may be combined where appropriate.

Chapters depend on the actual video, container and player. They are not guaranteed to exist.

## 5. Resolve conflicts and display the button

- Explicit Kodi chapter labels are strongest because they describe the actual file being played.
- Community sources are compared using release-duration match, confidence and submission count.
- Every distinct interval from the selected provider is retained; a credits sequence can therefore contain more than one skippable interval.
- Unnamed chapter heuristics remain Ask-only.
- The default behavior is **Ask**. Auto-skip remains limited to qualifying IntroDB evidence and the existing safety checks; TheIntroDB and chapter guesses do not silently trigger automatic seeking.

If no provider has a trustworthy interval, IntroSkip shows no button rather than inventing a timestamp.

## What IntroSkip does not do

It does not read or download subtitles, use subtitle phrase detection, require an OMDb/TVDB API key for reads, or maintain a personal viewing history. The local SQLite database is the public IntroDB snapshot, not a database of the user's library or watched titles.

If a provider does not expose enough information, it is normal for IntroSkip to show no button. See [Troubleshooting](TROUBLESHOOTING.md).
