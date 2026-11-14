# Troubleshooting

## No skip button appears

1. Confirm the relevant segment is enabled under **Detection**.
2. Set its behavior to **Ask** while testing.
3. Try another episode or movie. Not every title has community timestamps or useful chapter markers.
4. Confirm the title is identifiable. Cinemeta rejects ambiguous matches rather than guessing.
5. Check the Kodi log for IntroSkip messages around the time playback starts.

Kodi chapter detection only works when the playing file exposes chapter information.

## The skip time is wrong

Different releases of the same movie or episode can have different cuts and durations. IntroSkip compares available evidence and uses playback duration for TheIntroDB version matching, but a source may still differ.

Try another release of the title. If reporting a mismatch, include the title, season/episode and approximate expected and actual boundaries.

## IntroDB data is not available

IntroSkip keeps the last valid local database if a download fails. It defers checking the daily manifest until Kodi has been idle without playback or user input for two minutes, then refreshes the snapshot only when it changes.

A missing local record can trigger the single-item IntroDB API fallback. Network failures do not disable Kodi chapter detection or TheIntroDB.

## Preview segments are not detected

Under **Detection**, enable **Previews** (off by default). Previews require either a TheIntroDB v4 timestamp or an explicitly named native chapter such as "Next Episode Preview". IntroDB does not publish previews. TheIntroDB and chapter-based previews use the confirmation button even if Auto is selected. Generic chapters are not treated as previews.

## Kodi freezes on in-place updates or uninstalling

If Kodi becomes unresponsive, restart Kodi instead of manually deleting installed add-on files. Record the Kodi version, IntroSkip version, whether playback was active, and whether Kodi had been idle long enough for a background IntroDB sync. Include log lines mentioning "Shutdown:" and "CPythonInvoker" in an issue, with private stream addresses removed. Automated tests do not prove every platform will unload a running service successfully.

## TheIntroDB data is missing

TheIntroDB is an independent source and may not have data for every title or release. Its lookup uses the IMDb ID as a supported fallback and playback duration to select a version. Missing data from this source is normal and does not prevent other sources from working.

## The button is hard to read or covers controls

Open **Button appearance** and adjust the theme, color, position, size or style. Use **Preview button** before returning to playback.

## Report a problem

[Open an issue on GitHub](https://github.com/zoeywowy/service.introskip/issues/new) and include:

- Kodi version/build and device operating system
- IntroSkip version
- Movie or show name and season/episode, if relevant
- Steps to reproduce and expected versus actual behavior
- Relevant Kodi log lines, with private information removed

Never post private stream URLs, credentials, usernames or tokens.

For problems installing the repository, use the [repository troubleshooting guide](https://github.com/zoeywowy/repository.introskip/blob/main/docs/INSTALLATION.md).
