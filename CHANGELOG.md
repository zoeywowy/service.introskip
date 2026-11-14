# IntroSkip release notes

## 0.0.31 — Native preview detection and background worker lifecycle

**13 November 2026 · Kodi 22 pre-release**

- Recognize explicitly named Kodi 22 preview/next-episode chapters and retain multiple distinct preview intervals; reject ambiguous or excessively long candidates.
- Honor the existing Preview detection toggle in initial and delayed chapter checks; preserve Ask-only behavior for TheIntroDB and chapter matches.
- Fix a stale Requests exception reference in the standard-library IntroDB HTTP fallback.
- Synchronize lazy IntroDB adapter initialization and cancel/join the independent open-data worker during shutdown using a shared bounded wait.
- Add tests for native and community previews, HTTP failures, adapter reuse and thread termination; improve shutdown logging.
- Real-device Kodi in-place updates and uninstallations still require manual verification.


## 0.0.30 — Kodi update and uninstall lifecycle

**13 November 2026 · Kodi 22 pre-release**

- Instantiate Kodi's native skip-dialog window only when a skip prompt is actually shown, not at service startup or playback metadata initialization.
- On service shutdown, close the dialog and break its native Python/C++ reference cycle.
- Track playback lookup threads and request cancellation before Kodi's five-second shutdown deadline.
- Interrupt ongoing SQLite snapshot validation and index operations if Kodi disables, updates or stops IntroSkip.
- Add regression tests for idle service initialization, dialog teardown, worker cancellation and SQLite interruption.
- Preserve all IntroDB, TheIntroDB, native chapter and per-segment Ask/Auto detection features.

## 0.0.29 — Prompt shutdown on every device

**13 November 2026 · Kodi 22 pre-release**

- Bound Cinemeta, IntroDB, TheIntroDB and bulk-export HTTP waits to three seconds so an in-flight request cannot routinely outlast Kodi's five-second Python shutdown window.
- Keep the full IntroDB export off the startup path; refresh only after two minutes without playback or user input.
- Track whether the modeless skip dialog was actually opened. Shutdown no longer calls Kodi's GUI close operation for a dialog that was never shown.
- Add explicit shutdown-stage logging and tests for dialog lifecycle and bounded network timeouts.

## 0.0.28 — UI-idle sync guard

**12 November 2026 · Kodi 22 pre-release**

- Require both no active video playback and two minutes without Kodi remote or keyboard input before starting the bulk IntroDB refresh.
- Avoid starting background imports while users are navigating Kodi settings or menus.

## 0.0.27 — Low-resource installation and shutdown

**12 November 2026 · Kodi 22 pre-release**

- Removed the external `script.module.requests` dependency; all HTTP calls use Python's standard library.
- Deferred the full IntroDB snapshot refresh until Kodi has been idle without video playback for two minutes.
- Streamed compressed CSV downloads to disk instead of holding both exports in memory.
- Imported CSV files in small batches, yielding between batches to reduce CPU contention on Android TV and other low-power devices.
- Added cancellation checks during downloads and database construction; playback start and Kodi shutdown stop background work without waiting.
- Replaced playback-time full SQLite integrity scans with a lightweight schema check; full checks remain on newly built databases and background refresh.
- Reused Kodi's add-on settings wrapper rather than constructing it on every service-loop poll.
- Removed unused legacy helpers and redundant image assets.

## 0.0.26 — Reliability and release cleanup

**12 November 2026 · Kodi 22 pre-release**

- Validate the local IntroDB SQLite index before using it; rebuild a damaged cache even when the daily manifest is unchanged.
- Require valid SHA-256 checksums and reject malformed open-data rows before indexing.
- Build the SQLite lookup index after bulk import and verify database integrity before use.
- Synchronize playback state and segment access; prevent stale network results from crossing playback sessions.
- Add automated recovery coverage for a damaged local database.
- Refresh installation and project documentation to match the working Kodi repository installer.

## 0.0.25 — Multi-source detection

**12 November 2026 · Kodi 22 pre-release**

- Added IntroDB's complete daily open-data export and a local SQLite lookup index.
- Retained the single-episode IntroDB API as a fallback when the snapshot is unavailable or has no record.
- Added TheIntroDB v4 with playback-duration matching, multiple timestamp intervals and optional preview prompts.
- Kept Kodi 22 native chapter detection independent; explicit chapter labels retain priority.
- Added keyless Cinemeta title resolution and retained per-segment Ask/Auto settings.
- Kept TheIntroDB and chapter-only matches confirmation-only for automatic skipping.
- Added the required IntroDB ODbL attribution.

## 0.0.24 — Kodi 22 compatibility

- Set the Kodi Python dependency for Kodi 22.
- Separated the service add-on from the Kodi repository project.
- Simplified the service ZIP build and retained Cinemeta, IntroDB, native chapters and button customization.

## Earlier releases

See [HISTORY.md](HISTORY.md) for archived development notes. Historical entries describe older builds and may mention features that are no longer part of IntroSkip.
