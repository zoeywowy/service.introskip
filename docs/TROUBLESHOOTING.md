# Troubleshooting and support

## No skip button

- Check that the relevant segment type is enabled under **Detection**.
- Some media does not have verified IntroDB timestamps or explicitly named Kodi chapters. IntroSkip intentionally does not invent timestamps.
- Cinemeta must find an unambiguous IMDb title match. Unusual titles, remakes, missing movie years or limited player metadata can prevent resolution.
- Try a different episode or movie with clearly named chapters. External services can be unavailable.
- Set the action to **Ask** while verifying playback.

## The skip boundary is inaccurate

IntroDB timestamps may be based on a different edit/cut of the content. Kodi 22 explicit local chapters are preferred when available. Report the title, season/episode and approximate time mismatch; don't include video streaming URLs or account credentials.

## Settings and UI

If buttons overlap your video controls, adjust Button appearance → position/size and use Preview. Test Light/Dark with your skin.

## Bug report

Open an [Issue](https://github.com/zoeywowy/service.introskip/issues/new) and include:

- Kodi exact version/build and operating system/device.
- IntroSkip version (for example 0.0.23).
- Whether the problem involves Cinemeta lookup, IntroDB, Kodi chapters, or button display.
- Example movie/show title and season/episode (but **not** a private stream URL).
- Expected vs actual result and steps to reproduce.
- Relevant `kodi.log` lines with usernames, tokens, stream URLs, and personal information removed.

## Current testing status

Unit tests use mocked Kodi APIs. Live device/provider compatibility has **not** yet been independently verified for 0.0.23.
