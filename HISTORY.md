# Archived release notes

This file preserves the original detailed build notes through version 0.0.20.

## 0.0.20
- Always-on Kodi 22 chapter detection and concurrent IntroDB lookup.
- Removed OMDb API settings, title lookup, and cache code.
- Moved detection notifications and chapter inspector to Advanced.
- Renamed Button theme / Button color; limited colors to readable theme-specific choices.
- Removed high-contrast toggle; stopped the duplicate XML button flash and marquee text.
- Preserved the 0.0.19 matte textures, viewer overrides, recap/outro and per-segment Ask/Auto.

## 0.0.19
- Replaced blue bordered button art with modern flat matte gradient borderless PNG buttons.
- Removed transparency setting and old button asset pipeline.
- Polished settings labels and appearance section.

## 0.0.18 — IntroDB and Kodi 22 chapters only (2026-11-12)

- Removed a4kSubtitles integration, bundled `pysrt` and subtitle-related
  detection, file parsers, learned matching/cache, late-file probes and
  subtitle stream events/diagnostics.
- Retained Kodi 22 native chapter API, complete per-chapter log output,
  chapter inspector, late chapter refreshes and chapter-only native events.
- Retained IntroDB, cached OMDb lookups, user local timestamp overrides,
  recap/outro/movie prompt modes and all 60 PNG button styles.
- Removed outdated settings entries for subtitle and gap logging.
- Did **not** delete or modify any existing add-on profile files or user data.

## 0.0.17 — Kodi 22 native event bridge (2026-11-12)

- Add a bundled, pure-Python `KodiNativeMonitor` that observes `Player.OnPropertyChanged` and queues relevant subtitle/chapter refreshes on the service thread, with bounded retries and existing scheduled checks retained.
- Read Kodi 22's native subtitle-stream metadata once per playback item for diagnostic logging (count, enabled state and selected state only); no subtitle dialogue or private media URLs logged.
- Expand episode-verified downloaded-subtitle lookup to both a4k's temporary cache and Kodi's own `special://temp/` staging location, which a4k can use depending on storage settings.
- Keep strict show, season, episode, recency, size and non-symlink checks; no automatic subtitle enabling or playback behavior changes.
- Require Kodi 22's Python interface. This does not unlock private C++ subtitle buffers or provide native subtitle cue text; that requires an upstream Kodi change.
- Retain IntroDB, complete Kodi 22 chapter logging, 60 PNG button textures, and per-segment skip policies.

## 0.0.16 — Kodi 22 subtitle handoff and retry (2026-11-12)

- Kodi 22 logs showed a4kSubtitles provider searches finding candidates while IntroSkip received no selectable subtitle rows. Avoid mistaking provider candidate counts for downloadable subtitle search results.
- Reuse a4kSubtitles' own *recently downloaded* SRT/WebVTT/ASS/SSA files when their names unambiguously match the current TV show, season and episode. Do not enable subtitles or alter user preferences.
- Refuse stale subtitle files, season-only packs without a matching episode number, and files for other shows.
- Make at most one quick/full provider-search sequence per playback item instead of repeating slow provider searches separately for intro, recap, and outro.
- Check local a4k files at four bounded playback times; if a subtitle arrives late, apply the existing intro/recap/outro logic without additional provider requests.
- Keep subtitle results confirmation-only; never change successful IntroDB, chapter, local override, or PNG-button behavior.
- Add INFO-level logs for selected subtitle source, parsed cue count, delayed local checks, and unselectable a4k search results (no subtitle dialogue or API tokens in logs).
- Does not fix unavailable subtitle providers or identify subtitle text embedded in media files that Kodi cannot expose.

## 0.0.15 — Kodi 22 subtitle fallback expansion (2026-11-12)

- Added lightweight SRT, WebVTT and ASS/SSA readers for a4kSubtitles results (no external binaries or media decoding).
- Parse and log the downloaded subtitle format and cue count for diagnosing missed fallbacks.
- Normalize Kodi 22 BCP-47 subtitle language tags such as `en-US` and `es-MX` when querying providers.
- Preserve music cues used by intro matching; avoid dropping dialogue just because it contains substrings such as `sub` or `caption`.
- Keep subtitle cues in chronological order even when a subtitle provider returns them out of sequence.
- Separate recap phrases from intro keyword scoring to reduce cross-segment confusion.
- Prefer an early strong recap-ending pause over weaker montage gaps while retaining the existing weaker-gap fallback; maintain ask-only subtitle matches.
- Do not treat mentions of post-credit scenes as reliable closing-credit skip cues.
- Retained Kodi 22 complete chapter logging, chapter inspector, 60 PNG textures and opt-in IntroDB auto-skip.

## 0.0.14 (Kodi 22 feature build)
- Use Kodi 22 JSON-RPC `Player.GetChapters` as the authoritative source of complete chapter names and timestamps. It returns integer seconds.
- At INFO log level, record each `Player.GetChapters` fetch and EVERY raw chapter record (name, index, timestamp, and rejected/usable status), plus an empty-result message and summary. This works without Kodi debug logging.
- Replace invalid `Player.GetProperties(chapters)` and invented indexed InfoLabels.
- Refresh the complete chapter list at 2.5, 6, and 12 seconds after playback begins, even if an earlier query returned a partial list. Each fetch logs ALL chapter records at INFO level, including unnamed/invalid entries and rejection reasons. No continuous polling.
- Add a TV-remote-friendly Inspect Playing Chapters action and independent chapter detection switch in General settings.
- Identify unlabeled chapters separately from explicitly labeled intros/recaps/credits/post-credit scenes; never auto-skip chapters.
- Recognize generic end-credit labels, protect post-credit scenes from being treated as credits.
- Keep the existing IntroDB/OMDb/a4kSubtitles logic, auto skip, and PNG customization unchanged.
- Tests run using mock Kodi APIs; actual hardware behavior still needs verification.

## 0.0.13 — Preview and fallback reliability
- Preview action now closes/saves Kodi add-on settings before rendering, then reopens settings.
- Removed forced focus on the hidden fallback XML button that caused Kodi errors.
- Fixed the actual IntroSkip fallback crash: subtitle detection returned a list of intervals, but two success logs indexed it as two separate elements.
- Cache training exceptions no longer discard otherwise valid learned intro matches.
- Added bounded, ask-only subtitle-cue fallbacks for recaps and TV/movie closing credits.
- Reuse downloaded subtitle text for multiple segment windows in a playback session.
- Try chapter/subtitle fallback even when streaming metadata lacks an IMDb ID.
- Clear diagnostics when source exposes no chapters or caption cues; include traceback detail with Kodi debug logging.
- Preserve existing PNG textures, preferences, and source-specific safety policies.

## 0.0.12 - Fire TV usability corrections
- Repaired missing recap settings text (PO entry separation and localized string value).
- Replaced fragile XML group repositioning with Kodi native ControlButton using shipped PNG skins.
- Packaged rounded/square/minimal PNG textures in both themes, five alpha levels and focus states; all generated at build time, not on the Kodi device.
- Retained position, size, contents, accents, preview, and layout reset.
- Replaced built-in notification with native Kodi Dialog.notification and added detection summary after episode lookup.
- Fixed opt-in automatic skipping of IntroDB timestamps with only one submission; manual chapter/subtitle prompts preserved.
- Kept 0.0.11 as rollback; no profile or learned subtitle data is modified by the package.

# Changelog

## 0.0.11 — Feature build (Kodi-device testing pending)

- Use one shared remote-friendly prompt for TV recaps, intros, TV outro credits and movie credits.
- Add opt-in recap, TV outro and movie-credit toggles; preserve existing TV outro toggle and existing intro defaults.
- Add per-segment Ask vs Auto mode. Auto is opt-in and applies only to local timing overrides or IntroDB entries with confidence >= 0.90 and >= 3 submissions; fallback detectors remain prompt-only.
- Add explicit-chapter-title fallback for recap, outro and movie credits. Preserve the existing intro chapter heuristics and a4kSubtitles gap detector unchanged.
- Add IntroDB movie lookup with `is_movie=true`, plus a named-chapter fallback when movie IMDb metadata is missing. Protect known post-credit scene start times.
- Cache chapter inspection during a playback item to avoid repeating Kodi chapter queries for each segment.
- Add size, corner position, background style, opacity, icon/text and high-contrast customization, plus button preview and layout reset actions.
- Preserve saved subtitle patterns, existing API keys and legacy customization settings.
- No silent-credits or post-credit inference: uncertain recaps/credits are not automatically detected from subtitle silence.


## 0.0.10

- Read IntroDB's episode response once for intro, recap, and outro lookups.
- Parse IntroDB millisecond timestamp fields when second fields are unavailable.
- Read IntroDB community-confirmed absence flags without suppressing intro fallback detection for source-specific edits.
- Briefly cache failed IntroDB lookups to avoid repeating a slow request for each segment during the same playback start.
- Use a4kSubtitles `quick_search()` when the installed API provides it, then fall back to full search if quick results are unusable.
- Normalize subtitle language values to the language-name format expected by a4kSubtitles.
- Add a 90-day local cache for successful OMDb series IMDb lookups.
- Narrow OMDb title searches with the TV series premiere year when Kodi's library provides it.
- Correct the OMDb setting label and detection-notification wording.
