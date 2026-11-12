# Troubleshooting IntroSkip

## Repository ZIP browser is empty

If Kodi's **Install from zip file** browser shows only `..` and `0 items`, you have opened the GitHub Pages download webpage as though it were a folder. Kodi cannot browse the download button inside that HTML page.

1. Cancel the empty browser.
2. Open the [IntroSkip download page](https://zoeywowy.github.io/repository.introskip/) in a normal browser.
3. Download `repository.introskip-1.0.4.zip`. Do not extract it.
4. In Kodi, open **Add-ons → Install from zip file** and browse to the ZIP in Downloads, USB storage or a network share.

Do not add `https://zoeywowy.github.io/repository.introskip/` as a Kodi File Manager source.

## Repository won't connect after installation

If Kodi says **“Could not connect to repository”** after the repository ZIP has installed, it is failing to read the repository feed. That does not, by itself, mean the IntroSkip service is broken.

The repository installer lives in a separate project and follows the standard Kodi/A4K layout.

Check that these public files open in a browser:

- [Repository index](https://raw.githubusercontent.com/zoeywowy/repository.introskip/main/repo/zips/addons.xml)
- [Matching MD5 checksum](https://raw.githubusercontent.com/zoeywowy/repository.introskip/main/repo/zips/addons.xml.md5)
- [Repository installer source](https://github.com/zoeywowy/repository.introskip/tree/main/repo/repository.introskip)
- [Generated service package](https://github.com/zoeywowy/repository.introskip/tree/main/repo/zips/service.introskip)

The repository manifest uses `info compressed="false"`, the matching `addons.xml.md5`, and `datadir zip="true"`. Do not use the old `https://zoeywowy.github.io/service.introskip/` address.

If an older repository add-on is installed, uninstall only **IntroSkip Repository** (ID `repository.introskip`) before installing the new one. Do not uninstall **IntroSkip** (ID `service.introskip`) or clear its settings.

If Kodi still cannot connect, capture a fresh `kodi.log` immediately after reproducing the error. Look for `repository.introskip`, `addons.xml`, `CCurlFile`, `GetDirectory`, `ERROR`, or `WARNING`. The fresh log will show whether Kodi is using an old URL or failing on the new raw GitHub endpoint.

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
