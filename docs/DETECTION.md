# How IntroSkip detects segments

IntroSkip combines three independent sources: **IntroDB**, **TheIntroDB v4**, and **Kodi 22 native chapters**. **Cinemeta** resolves the playing title to an IMDb ID so the community sources can be queried.

## 1. Identify the playing item

Kodi supplies the media type, title and, for TV, season and episode. If the title tag is unavailable, IntroSkip can try the filename. Cinemeta checks the title, media type and movie year when available. Ambiguous matches are rejected.

IntroSkip does not use OMDb, Kodi library-ID searches or provider API keys.

## 2. IntroDB: daily local data

IntroDB publishes a daily open-data snapshot containing live segment timestamps and confirmed segmentless entries.

To keep low-power devices responsive, the full snapshot refresh is deferred until Kodi has had no video playback and no remote or keyboard input for two minutes. Downloads stream to disk, are checksum-verified and are processed in small batches. The local SQLite index is built in a background worker and atomically replaced only after validation. A refresh is cancelled when playback starts or Kodi shuts down. If the snapshot is not ready, the single-item IntroDB API fallback remains available.

When a title is playing, its IMDb ID and episode coordinates are looked up locally. The single-item IntroDB API is the fallback when the snapshot is unavailable or has no record for that item.

## 3. TheIntroDB v4: independent live data

IntroSkip also queries TheIntroDB v4 with the IMDb ID, episode coordinates and actual playback duration. The API prefers TVDB identity but supports IMDb as a fallback. Duration matching helps select the closest release version.

The adapter preserves multiple valid intro, recap, credits and preview intervals. Responses are cached locally for seven days. A failure or missing record from this source does not stop the other detectors.

## 4. Kodi 22 chapters: local file information

Kodi's `Player.GetChapters` API exposes chapter indexes, names and start positions in seconds. IntroSkip recognizes clear labels such as opening credits, recap and end credits. Adjacent named opening chapters can be combined when safe.

Chapter information depends on the actual file, container and player. Some streams expose no chapters.

## 5. Choose the best evidence

- Explicitly named Kodi chapters describe the playing file and have the highest priority.
- IntroDB and TheIntroDB are compared using release-duration match, confidence and submission count.
- All distinct intervals from the selected community source are retained.
- Unnamed chapter heuristics are confirmation-only.
- **Ask** is the default. **Auto** is restricted to qualifying IntroDB data and the existing safety checks. TheIntroDB and chapter-only matches never trigger automatic seeking.

Movie credits are treated conservatively to avoid skipping a known post-credit scene.

## Data and privacy

IntroDB's local index and TheIntroDB's cache contain public timestamp data, not a personal library or viewing history. IntroSkip does not inspect subtitles.

IntroDB data is published under ODbL 1.0. Attribution: **"Contains data from IntroDB (introdb.app), available under the ODbL."**

[IntroDB open data](https://api.introdb.app/open-data/) · [IntroDB API](https://api.introdb.app/) · [TheIntroDB API](https://theintrodb.org/docs)
