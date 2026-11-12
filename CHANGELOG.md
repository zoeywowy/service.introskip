# IntroSkip — Release Notes

## v0.0.24 — Kodi 22 installation compatibility
**12 November 2026 · Pre-release**

- Corrected the minimum `xbmc.python` requirement from **3.1.1** to **3.1.0**, matching Kodi 22's published Python add-on manifest.
- Declared a minimum `script.module.requests` version and added clearer add-on metadata.
- Updated the Kodi repository installer to **1.0.1** and included artwork alongside the hosted ZIPs.
- Rewrote installation, troubleshooting and contributor documentation for the current build.
- Cinemeta, IntroDB, native chapter detection, Ask/Auto behavior and button appearance are unchanged.
- The repository connection problem still needs real-device confirmation: a browser displaying `addons.xml` does not prove Kodi can access or parse it.

---

A Kodi 22 skip-button service with **Cinemeta + IntroDB + native chapters**, readable theme palettes and minimal settings.

---

## 🎬 v0.0.23 — Keyless identification, cleaner interface
**12 November 2026 · Kodi 22 / Fire TV**

### One automatic ID source
- **Cinemeta** now searches movie and TV series titles for an IMDb ID, requiring **zero API keys** and no Stremio or additional Kodi add-ons.
- Strict **media type, title, and movie-year checks** prevent inappropriate search results from being mistaken for the requested item. A series' IMDb ID is passed to IntroDB together with its season and episode.
- Removed **OMDb** code, its key field, and all direct **Kodi library IMDb-ID searches**. Kodi still supplies basic playing-item title/season/episode metadata.

### Simpler settings
- Removed the **Advanced tab** and both **chapter inspector** and **playback diagnostics** actions.
- Moved **Show detection notifications** into Detection; previous preference persists because its setting ID is unchanged.
- Kept separate, readable **Light and Dark button color palettes**, styles, sizes, positions, and working preview/reset tools.

### Safer & lighter playback
- Cinemeta/IntroDB lookup runs off the playback thread and hands results to the service thread.
- Kodi 22 chapter detection still operates independently and wins when explicit source-local markers disagree with remote timestamps.
- No persistent timestamp caching, ID history, or subtitle reading.
- Legacy settings and user data are left untouched rather than erased.

---

## 🚀 v0.0.22 — Better identification, less waiting
**12 November 2026 · Kodi 22 / Fire TV**

### Identification
- Restored **optional OMDb API key** in Advanced. Uses series-level IMDb IDs for TV and movie IMDb IDs for films.
- OMDb requests run on a background worker and validate title/type/year; Kodi chapters never wait for the network.
- **No TVDB scraper dependency.** No bundled credentials, no title guesses, and no metadata crawling.

### Interface
- Two independent, readable **Light/Dark button color palettes** with color-coded selections.
- Added **Playback diagnostics** to Advanced. Shows session-only current video, IMDb origin, OMDb status, IntroDB status, chapter count and chosen skip ranges.

### Performance and reliability
- Stops scheduled chapter re-fetches once a complete usable chapter list has arrived; still listens for chapter-change events.
- Merges adjacent explicitly named intro chapters (e.g. *Opening Credits* + *Title Sequence*) when safe.
- Removed IntroDB's cross-episode timestamp LRU and negative-result cache. Current playback requests run once; no persistent timestamp data is saved.

### Preservation
- Existing styles, positions, Ask/Auto preferences, notification setting, and Chapter Inspector remain.
- Previous userdata and old cached files are not automatically deleted.
- The scraper dependencies are **not** installed or required.

---

## ✨ v0.0.21 — Focused & polished
**12 November 2026 · Kodi 22 · Fire TV / Android / Desktop**

### New
- **Enable intro detection:** Control intros independently of recaps and credits; on by default.
- **Button color:** A native Kodi selector with seven readable colors. Each maps to a brighter shade for Dark and a deeper shade for Light.

### Improved
- **No detection-source switches:** IntroDB and Kodi 22 chapters both remain active. Explicitly named chapters take precedence when different video cuts disagree.
- **Cleaner settings:** Detection controls only the segment types; skip preferences and button appearance stay in their own sections; diagnostics remain in Advanced.
- **Faster, simpler detection:** Removed local-override reads and discontinued a redundant provider setting. Chapter detection never depends on an IMDb match.
- **Better traceability:** Button logs now report theme and selected text color; the complete chapter inspector and chapter logging remain available.

### Removed
- Viewer-maintained manual timestamp detection and its bundled parser.
- The former separate color-picker script action and hidden text-color preference.
- The **Use IntroDB** option (IntroDB remains always on).

**Privacy / migration:** IntroSkip does not erase older userdata. Old local timestamp files are simply no longer read. Existing Ask/Auto preferences and PNG styles are retained.

---

## 🎨 v0.0.20 — Native-first playback
- Parallel IntroDB lookups and Kodi 22 chapter checks, with named chapters winning over cross-cut community timestamps.
- Prefetch IntroDB metadata when Kodi supplies trustworthy episode information before AV starts.
- Removed OMDb dependency and settings. Moved detection notifications and Chapter Inspector to Advanced.
- Fixed the first-frame skip-button position/size jump and scrolling labels.

## 🖌️ v0.0.19 — Modern button redesign
- Flat matte gradient buttons in Light/Dark and Pill/Soft/Flat styles.
- Removed blue-outline artwork, transparency control and legacy textures.

## 🔎 v0.0.18 — Dependable detection sources
- Removed subtitle detection, a4kSubtitles handoffs, subtitle learning and related dependencies.
- Kept IntroDB and Kodi 22 native chapters, including full chapter logs and delayed refreshes.

## 📚 Older releases
The [archived release history](HISTORY.md) retains the original implementation notes for v0.0.9–v0.0.20.
