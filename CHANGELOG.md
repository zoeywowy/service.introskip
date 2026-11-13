# IntroSkip release notes

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
