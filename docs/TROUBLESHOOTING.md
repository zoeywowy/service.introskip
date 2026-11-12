# Troubleshooting IntroSkip

## Repository ZIP browser is empty

If Kodi's **Install from zip file** browser shows only `..` and `0 items`, you have opened the GitHub Pages download webpage as though it were a folder. Kodi cannot browse the download button inside that HTML page.

1. Cancel the empty browser.
2. Open the [IntroSkip download page](https://zoeywowy.github.io/repository.introskip/) in a normal browser.
3. Download `repository.introskip-1.0.4.zip`. Do not extract it.
4. In Kodi, open **Add-ons → Install from zip file** and browse to the ZIP in Downloads, USB storage or a network share.

Do not add `https://zoeywowy.github.io/repository.introskip/` as a Kodi File Manager source.

## Install from ZIP shows an empty folder

If Kodi's **Install from zip file** window shows only `..` and **0 items**, it is browsing an empty location. The GitHub Pages URL is an HTML download page, not a browseable ZIP directory.

1. Open the [IntroSkip download page](https://zoeywowy.github.io/repository.introskip/) in a normal web browser.
2. Download `repository.introskip-1.0.4.zip`. Do not extract it.
3. Make the ZIP accessible to Kodi (Downloads on Windows, or local/shared storage on Android and Fire TV).
4. Return to Kodi's **Install from zip file** browser and select the local folder containing the ZIP.

**Do not add the GitHub Pages URL as a Kodi File Manager source.** Kodi cannot browse the HTML download page.

Do not uninstall the IntroSkip service or clear its settings to solve an empty file picker.

## IntroSkip is installed, but no skip button appears

- Check **Detection** and enable the relevant segment. By default, intro is enabled, while recap and credits are off.
- Set the segment's behavior to **Ask** for testing.
- IntroDB may have no timestamps for that title, or the current video may not expose useful named chapters.
- Cinemeta must identify the title unambiguously. If it cannot, IntroDB will not be used for that item, although named Kodi chapters may still work.
- Test another episode or video. Different editions of the same title can have different timing.

## Skip time is inaccurate

Community timestamps may have been measured on another cut or edition. Explicitly named Kodi chapters are preferred where available. If you report a mismatch, include the title and approximate expected/actual start and end times.

## Button is hard to read or covers the controls

Use **Button appearance** to adjust the position, size, theme or color. Try **Preview button**. Light and Dark themes remember separate color choices.

## Report a bug

[Open a GitHub issue](https://github.com/zoeywowy/service.introskip/issues/new) with:

- Exact Kodi version/build and device operating system.
- IntroSkip or IntroSkip Repository version.
- The steps you took and the exact error message.
- What you expected to happen and what happened.
- Relevant redacted Kodi log lines.

For playback issues, include the movie or show name and season/episode if helpful. **Do not post private streaming URLs, credentials or personal information.**

## Testing status

Version 0.0.24 has automated tests using Kodi stubs. Real-device behavior, including Kodi 22 prerelease builds and third-party providers, still needs validation.
