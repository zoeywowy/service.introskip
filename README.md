# IntroSkip

**Skip intros, recaps, previews and credits in Kodi 22.**

IntroSkip is a lightweight Kodi background service. It combines community timestamps with Kodi's native chapter information and presents a customizable skip button when a reliable segment is found.

**Current build:** 0.0.29 · Kodi 22 pre-release

## Install

The recommended installation uses the IntroSkip Kodi repository:

1. In Kodi, open **Settings → File manager → Add source**.
2. Add `https://zoeywowy.github.io/repository.introskip/` and name it **IntroSkip Repository**.
3. Open **Add-ons → Install from zip file → IntroSkip Repository**.
4. Install the repository ZIP shown by Kodi.
5. Open **Add-ons → Install from repository → IntroSkip Repository → Services → IntroSkip** and install.

See the [complete installation guide](docs/INSTALLATION.md) or the [repository guide](https://github.com/zoeywowy/repository.introskip/blob/main/docs/INSTALLATION.md).

For a one-time direct installation without repository updates, use the latest installable ZIP in [GitHub Releases](https://github.com/zoeywowy/service.introskip/releases). Choose the release **Asset**, not GitHub's generated source archive.

## Detection

IntroSkip uses three independent sources:

- **IntroDB:** a daily open-data snapshot indexed locally with SQLite, plus a single-item API fallback.
- **TheIntroDB v4:** a second community source. Playback duration helps select the closest release version; multiple intervals and previews are supported.
- **Kodi 22 chapters:** reads chapter names and boundaries exposed by the playing file. Explicit chapter labels take priority over community timestamps.

**Cinemeta** resolves the playing title to an IMDb ID without an API key. Network lookups run in the background and never hold up playback.

IntroSkip validates segment boundaries and avoids guessing when a title or timestamp is uncertain. It does not read subtitles or require OMDb, TVDB or provider API keys.

[How detection works](docs/DETECTION.md)

## Settings

| Section | Options |
| --- | --- |
| Detection | Intros, recaps, previews, TV credits, movie credits and notifications |
| Skip behavior | Ask or Auto for each enabled segment |
| Button appearance | Light/Dark theme, color, position, size, style and content |

Defaults: intro detection is on; other segment types are off. All actions default to **Ask**. Auto-skip is deliberately conservative: only qualifying IntroDB data is eligible; TheIntroDB and chapter-based matches remain confirmation-only.

[Settings guide](docs/SETTINGS.md)

## Compatibility

- Designed for **Kodi 22 (Piers)** and its **Python 3.14** runtime.
- Uses Kodi's Python add-on interface and Python's standard library; no third-party Python add-ons are required.
- Chapter detection depends on the chapter information exposed by the actual video source.
- IntroSkip is a third-party add-on, not part of Kodi's official repository.

This is a pre-release. Automated tests cover the core logic, but device and playback-source testing is still important.

## Data and privacy

IntroSkip sends the playing title to Cinemeta for identification. When a match is found, it sends the IMDb ID and relevant episode/duration details to IntroDB and TheIntroDB.

The local IntroDB index and TheIntroDB response cache contain public timestamp data, not viewing history or contributor accounts. Kodi logs can contain media titles and network errors; redact personal information and private stream URLs before sharing logs.

IntroDB data is available under ODbL 1.0. Required attribution:

> Contains data from IntroDB (introdb.app), available under the ODbL.

[IntroDB open-data terms](https://api.introdb.app/open-data/) · [TheIntroDB API documentation](https://theintrodb.org/docs)

## Development

Run the test suites in separate processes because each provides its own Kodi test stubs:

```bash
python -m unittest discover -s tests -p 'test_023_integration.py' -v
python -m unittest discover -s tests -p 'test_023_chapters.py' -v
python build_zip.py
```

The installable service ZIP is written to `dist/`. The Kodi repository is built separately in [repository.introskip](https://github.com/zoeywowy/repository.introskip).

[Release notes](CHANGELOG.md) · [Troubleshooting](docs/TROUBLESHOOTING.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)
