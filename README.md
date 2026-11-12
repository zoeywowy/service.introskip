# IntroSkip for Kodi 22

Skip intros, recaps and credits in Kodi without setting up an API key.

IntroSkip is a small background add-on for TV shows and movies. When it finds a supported segment, it offers a **Skip Intro**, **Skip Recap**, or **Skip Credits** button. You can choose to press the button yourself, or allow certain verified segments to skip automatically.

**Current build: 0.0.24 (preview).** Built for Kodi 22, including Android and Fire TV. Device compatibility and detection accuracy still need real-world testing.

## Install

**Option 1 — Install from the Kodi repository**

1. In Kodi, open **Settings → File manager → Add source**.
2. Enter `https://zoeywowy.github.io/repository.introskip/` and name it **IntroSkip Repository**.
3. Open **Add-ons → Install from zip file → IntroSkip Repository** and select `repository.introskip-1.0.4.zip`.
4. Go to **Add-ons → Install from repository → IntroSkip Repository → Services → IntroSkip → Install**.

**Option 2 — Install directly**

Download [service.introskip-0.0.24.zip](https://github.com/zoeywowy/service.introskip/releases/download/v0.0.24/service.introskip-0.0.24.zip) and install it using **Add-ons → Install from zip file**. Choose the ZIP under **Release assets**, not GitHub's **Source code** archive.

The repository installer and package feed now live in the separate [repository.introskip project](https://github.com/zoeywowy/repository.introskip). It follows the standard Kodi/A4K layout: raw GitHub `addons.xml`, a matching `addons.xml.md5`, and versioned ZIPs under `addon.id/addon.id-version.zip` with `datadir zip="true"`. GitHub Pages is used only for the first-install repository ZIP. See the [installation guide](docs/INSTALLATION.md) if you need help.

[Step-by-step installation](docs/INSTALLATION.md) · [Troubleshooting](docs/TROUBLESHOOTING.md)

## What IntroSkip does

- **Intros, recaps and credits:** enable the segment types you care about.
- **IntroDB timestamps:** look for community-provided skip boundaries for a matching show or movie.
- **Kodi 22 chapters:** use recognizable chapter names when the playing video supplies them, even if online lookups are unavailable.
- **Cinemeta lookup:** identify a title by name to find its IMDb ID for IntroDB. No Cinemeta account, Stremio installation, or API key is needed.
- **Ask or Auto:** choose how to handle each segment. Automatic skipping is conservative; chapter-only matches do not auto-skip.
- **Custom skip buttons:** choose Light or Dark appearance, color, size, position and style, then preview the result.

Not every video has matching data. IntroSkip avoids guessing when identification or skip boundaries are uncertain.

## Settings at a glance

In **Add-ons → My add-ons → Services → IntroSkip → Configure**:

| Section | What you can change |
| --- | --- |
| Detection | Intro, recap, TV credits, movie credits, and detection notices |
| Skip behavior | Ask or Auto for each segment type |
| Button appearance | Theme, separate Light/Dark color choices, layout and preview |

**Defaults:** Intro detection is on; recap and credit detection are off. All skip actions start in **Ask** mode.

The current version has **no Advanced tab, OMDb key, subtitle detection, manual timestamp editor, or playback diagnostics button**. It does not use a persistent IMDb or timestamp cache.

[All settings](docs/SETTINGS.md) · [How detection works](docs/DETECTION.md)

## Compatibility and limitations

- Designed for **Kodi 22 with Python 3**; older Kodi versions are not the development target.
- Requires the Kodi Python runtime and the `script.module.requests` add-on dependency.
- Kodi chapters depend on what the player and video source expose; IntroDB coverage varies.
- IntroSkip is an **unofficial** add-on, not a listing in Kodi's official repository.
- Version 0.0.24 is a **pre-release**: automated tests are not a substitute for testing on a real player.

## Privacy

IntroSkip sends title-identification requests to Cinemeta and segment requests to IntroDB as needed. It does not inspect subtitles, save a persistent title/timestamp database, or ask for an API key. Kodi logs may include title names and network errors; redact personal information before sharing logs.

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

IntroSkip builds on earlier SubSkip work by **drinfernoo**. Data services: [Cinemeta](https://v3-cinemeta.strem.io/manifest.json) and [IntroDB](https://introdb.app/). Licensed under [Apache 2.0](LICENSE). Kodi, Cinemeta and IntroDB are independent projects.
