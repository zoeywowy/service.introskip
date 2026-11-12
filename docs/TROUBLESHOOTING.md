# Troubleshooting IntroSkip

## Repository won't connect

If Kodi says **“Could not connect to repository”**, that refers to downloading or reading the repository list. It does not, by itself, prove that the IntroSkip service is broken.

The previous repository installer (1.0.2) used a GitHub Pages index and a nonstandard plain-text checksum URL. Replace it with **IntroSkip Repository 1.0.3**, which now follows the standard Kodi/A4K repository layout.

1. Download [repository.introskip-1.0.3.zip](https://zoeywowy.github.io/service.introskip/repository.introskip-1.0.3.zip).
2. In Kodi, choose **Add-ons → Install from zip file** and select that ZIP. Install it over the existing repository add-on. If Kodi will not replace it, uninstall only **IntroSkip Repository** (ID `repository.introskip`) and then install 1.0.3. Do not uninstall **IntroSkip** (ID `service.introskip`) or clear its settings.
3. Confirm these public endpoints open in a browser:
   - [Repository index](https://raw.githubusercontent.com/zoeywowy/service.introskip/main/repository/zips/addons.xml)
   - [MD5 checksum](https://raw.githubusercontent.com/zoeywowy/service.introskip/main/repository/zips/addons.xml.md5)
   - [Repository package folder](https://github.com/zoeywowy/service.introskip/tree/main/repository/zips/repository.introskip)
   - [Service package folder](https://github.com/zoeywowy/service.introskip/tree/main/repository/zips/service.introskip)
4. The MD5 file should contain exactly 32 hexadecimal characters. Its value must match the MD5 of the downloaded `addons.xml` file.
5. Correct the typo seen in the earlier Kodi log (`services.introskip`, extra `s`, returned HTTP 404). The bootstrap page is `https://zoeywowy.github.io/service.introskip/`; the repository's actual index and package URLs are raw GitHub URLs.
6. Restart Kodi, then open **Add-ons → Install from repository → IntroSkip Repository** again.

If Kodi still cannot connect, capture a fresh `kodi.log` immediately after reproducing the error. Look for `repository.introskip`, `addons.xml`, `CCurlFile`, `GetDirectory`, `ERROR`, or `WARNING`. The fresh log will show whether Kodi is still using an old URL or failing on the new raw GitHub endpoint.

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
