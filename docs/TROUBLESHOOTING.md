# Troubleshooting IntroSkip

## Repository won't connect

If Kodi says **“Could not connect to repository”**, that refers to downloading or reading the repository list. It does not, by itself, prove that the IntroSkip service is broken.

1. On a browser, open the [repository index](https://zoeywowy.github.io/service.introskip/addons.xml). A message that the XML **“does not appear to have any style information”** is normal. You should see `<addons>` and entries for `repository.introskip` and `service.introskip`.
2. Check the [checksum file](https://zoeywowy.github.io/service.introskip/addons-checksum.txt) and the [repository installer ZIP](https://zoeywowy.github.io/service.introskip/repository.introskip-1.0.2.zip). The checksum should show plain text; the ZIP should download. A working index **alone** does not confirm every file is accessible.
3. Correct the typo seen in a Kodi log (`services.introskip`, extra `s`, returned HTTP 404). Make sure Kodi's File Manager source is exactly `https://zoeywowy.github.io/service.introskip/`, with **github.io**, not **github.com**. An installed repository also has its own URLs; changing the File Manager source alone does not rewrite an already installed repository add-on.
4. Restart Kodi, then use the add-on browser's **Check for updates** command if available. Verify that the device's date/time and internet access are correct. DNS, TLS certificates, VPNs, device connectivity and stale repository information can cause a mismatch between a phone browser and Kodi.
5. If you installed **IntroSkip Repository 1.0.1**, install **1.0.2**: a Kodi 22 log showed failures reading the old `addons.xml.md5` URL. Version 1.0.2 uses `addons-checksum.txt` instead. This is a targeted workaround pending Kodi verification. You do not need to delete IntroSkip's personal settings to do this.
6. Still failing? Try the [direct service ZIP](https://github.com/zoeywowy/service.introskip/releases/download/v0.0.24/service.introskip-0.0.24.zip) as a temporary alternative, then capture Kodi's log after reproducing the repository error.

**Important:** We have confirmed that the index loads in a browser, but that does not establish why your Kodi device still reports a connection failure. The relevant `kodi.log` entry is needed to tell whether the problem is a network response, bad checksum, invalid dependency, or failed index parsing.

Look for `repository.introskip`, `addons.xml`, `CCurlFile`, `GetDirectory`, `ERROR`, or `WARNING`. Never share stream addresses, tokens, usernames or passwords from the log.

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
