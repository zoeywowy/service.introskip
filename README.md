# IntroSkip for Kodi 22

Skip intros, recaps, previews and credits in Kodi with three independent community/local detection sources.

IntroSkip is a small background add-on for TV shows and movies. When it finds a supported segment, it offers a **Skip Intro**, **Skip Recap**, **Skip Preview**, or **Skip Credits** button. You can choose to press the button yourself, or allow certain verified segments to skip automatically.

**Current build: 0.0.25 (preview).** Built for Kodi 22, including Android and Fire TV. Device compatibility and detection accuracy still need real-world testing.

## Install

**Option 1 — Install from the Kodi repository**

1. Open the [IntroSkip download page](https://zoeywowy.github.io/repository.introskip/) in a normal web browser and download `repository.introskip-1.0.4.zip`. Do not extract it.
2. Make the ZIP available to Kodi. On Windows, leave it in Downloads; on Android/Fire TV, download it on the device or copy it over USB or a shared network folder.
3. In Kodi, open **Add-ons → Install from zip file** and browse to the downloaded ZIP.
4. After the repository installer is installed, open **Add-ons → Install from repository → IntroSkip Repository → Services → IntroSkip → Install**.

**Option 2 — Install directly**

Download [service.introskip-0.0.25.zip](https://github.com/zoeywowy/service.introskip/releases/download/v0.0.25/service.introskip-0.0.25.zip) and install it using **Add-ons → Install from zip file**. Choose the ZIP under **Release assets**, not GitHub's **Source code** archive.

The repository installer and package feed now live in the separate [repository.introskip project](https://github.com/zoeywowy/repository.introskip). It follows the standard Kodi/A4K layout: raw GitHub `addons.xml`, a matching `addons.xml.md5`, and versioned ZIPs under `addon.id/addon.id-version.zip` with `datadir zip="true"`. GitHub Pages is used only for the first-install repository ZIP. See the [installation guide](docs/INSTALLATION.md) if you need help.

[Step-by-step installation](docs/INSTALLATION.md) · [Troubleshooting](docs/TROUBLESHOOTING.md)

## What IntroSkip does

- **Intros, recaps, previews and credits:** enable the segment types you care about.
- **IntroDB open data:** download the complete daily community snapshot once, build a local SQLite index, and check its small manifest at each Kodi launch. The compressed data is refreshed only when the snapshot changes.
- **IntroDB live API:** retain the single-episode API as a fallback when the local snapshot is not available or does not contain the requested title.
- **TheIntroDB v4:** query a second independent community source using the IMDb ID and actual playback duration; preserve multiple timestamp ranges and optional preview segments.
- **Kodi 22 chapters:** use recognizable chapter names when the playing video supplies them, even if online lookups are unavailable.
- **Cinemeta lookup:** identify a title by name to find its IMDb ID. No Cinemeta account, Stremio installation, or API key is needed.
- **Ask or Auto:** choose how to handle each segment. Automatic skipping is conservative; chapter-only matches do not auto-skip.
- **Custom skip buttons:** choose Light or Dark appearance, color, size, position and style, then preview the result.

Not every video has matching data. IntroSkip avoids guessing when identification or skip boundaries are uncertain.

## Settings at a glance

In **Add-ons → My add-ons → Services → IntroSkip → Configure**:

| Section | What you can change |
| --- | --- |
| Detection | Intro, recap, preview, TV credits, movie credits, and detection notices |
| Skip behavior | Ask or Auto for each segment type |
| Button appearance | Theme, separate Light/Dark color choices, layout and preview |

**Defaults:** Intro detection is on; recap, preview and credit detection are off. All skip actions start in **Ask** mode.

The current version has **no Advanced tab, OMDb key, subtitle detection, manual timestamp editor, or playback diagnostics button**. It stores the public IntroDB open-data snapshot locally and caches TheIntroDB API responses for seven days to reduce repeated requests. It does not store a personal viewing history or a persistent IMDb title database.

[All settings](docs/SETTINGS.md) · [How detection works](docs/DETECTION.md)

## Compatibility and limitations

- Designed for **Kodi 22 with Python 3**; older Kodi versions are not the development target.
- Requires the Kodi Python runtime and the `script.module.requests` add-on dependency.
- Kodi chapters depend on what the player and video source expose; IntroDB coverage varies.
- IntroSkip is an **unofficial** add-on, not a listing in Kodi's official repository.
- Version 0.0.25 is a **pre-release**: automated tests are not a substitute for testing on a real player.
- TheIntroDB v4 currently uses IMDb as a supported fallback identity. Its API prefers TVDB IDs, but IntroSkip does not add Kodi library-ID lookups.

## Privacy

IntroSkip sends title-identification requests to Cinemeta and, when needed, segment requests to IntroDB and TheIntroDB. The daily IntroDB snapshot and TheIntroDB response cache are stored under Kodi's add-on profile; they contain public timestamp data, not account or contributor identities. IntroSkip does not inspect subtitles or require a provider API key for reads. Kodi logs may include title names and network errors; redact personal information before sharing logs.

The IntroDB snapshot is available under the Open Database License (ODbL 1.0). Attribution: **"Contains data from IntroDB (introdb.app), available under the ODbL."**

## For contributors

The add-on lives at the repository root; its core Python code is under `resources/`.

```bash
python -m unittest discover -s tests -p 'test_023_integration.py' -v
python -m unittest discover -s tests -p 'test_023_chapters.py' -v
python build_zip.py
```

The first two test suites should be run in **separate processes**. The service ZIP is built into `dist/`. Kodi repository packages are generated and published separately by [repository.introskip](https://github.com/zoeywowy/repository.introskip).

[Release history](CHANGELOG.md) · [Publishing guide](docs/PUBLISHING.md) · [Contributing](CONTRIBUTING.md) · [Report a problem](https://github.com/zoeywowy/service.introskip/issues/new)

## Credits

IntroSkip builds on earlier SubSkip work by **drinfernoo**. Data services: [Cinemeta](https://v3-cinemeta.strem.io/manifest.json), [IntroDB](https://introdb.app/) and [TheIntroDB](https://theintrodb.org/). Licensed under [Apache 2.0](LICENSE). Kodi, Cinemeta and IntroDB are independent projects.
