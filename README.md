# IntroSkip for Kodi 22

**Automatic intro, recap, outro and movie-credit skipping with Cinemeta, IntroDB and Kodi 22 named chapters.**

![Kodi](https://img.shields.io/badge/Kodi-22-blue) ![Python](https://img.shields.io/badge/Python-3-blue) ![Status](https://img.shields.io/badge/release-v0.0.23%20candidate-orange)

IntroSkip is a Python service add-on for Kodi. It can display customizable **Skip Intro**, **Skip Recap** and **Skip Credits** prompts. Users can select Ask or Auto behavior. Auto-skipping uses qualifying IntroDB segments; chapter-only detections are conservative.

> **Pre-release candidate:** v0.0.23 passed offline tests but has not been verified across real Kodi 22/Fire TV devices.

## Features

- Keyless **Cinemeta** movie and TV series identification via HTTPS, independent of Kodi library scraping.
- **IntroDB** skip ranges for recaps, intros and credits.
- **Kodi 22 named chapters**, independently of external services.
- Customizable modern remote-friendly buttons with separate Light/Dark palettes.
- No OMDb API key, TVDB plugin, subtitles or persistent timestamp cache.
- No Advanced diagnostics tab.

## Install

1. Download `service.introskip-0.0.23.zip` from **[Releases](https://github.com/zoeywowy/service.introskip/releases)** once the release asset is published. **Do not use the GitHub-generated "Source code (zip)" file to install in Kodi.**
2. Open Kodi 22 → **Add-ons → Install from zip file**.
3. Select the downloaded ZIP and install.
4. Restart Kodi and configure **Detection**, **Skip behavior**, and **Button appearance**.

Full guides: [Installation](docs/INSTALLATION.md), [Detection](docs/DETECTION.md), [Settings](docs/SETTINGS.md), [Troubleshooting](docs/TROUBLESHOOTING.md).

## How it works

```text
Kodi playback title + media type (+ season/episode for TV)
 ├─ Kodi 22 native named chapters (independent, offline)
 └─ Cinemeta title search → verified IMDb ID → IntroDB skip times
                                                    ↓
                                              Skip button
```

Cinemeta is a **Stremio metadata service**, not a Kodi add-on; no Stremio installation is needed. Search matches are checked against the requested title and media type, and movie year if available. If lookup fails, native Kodi chapters may still supply skip markers.

## Compatibility and privacy

Designed for **Kodi 22** and Python 3, particularly on Android and Fire TV; older Kodi releases are not a focus. Playback results depend on available metadata, provider, stream chapters and external services. IntroSkip contacts **Cinemeta** and **IntroDB** over HTTPS when needed. It does not write a persistent timestamp/IMDb cache. Logs may include title and lookup details.

## Source and tests

Once the source files are uploaded, use `addon.xml`, `service.py`, `main.py` and `resources/` from the repository root; `tests/` contains Kodi-stubbed offline checks.

```bash
python -m unittest discover -s tests -p 'test_023_integration.py' -v
python -m unittest discover -s tests -p 'test_023_chapters.py' -v
python build_zip.py
```

The ZIP builder produces an installable archive with a `service.introskip/` root. The source repository and the release's installable ZIP are distinct artifacts.

## Community

Please [report a bug](https://github.com/zoeywowy/service.introskip/issues) with Kodi version, device, steps and a redacted log. See [Contributing](CONTRIBUTING.md), [Security](SECURITY.md), [Changelog](CHANGELOG.md) and [License](LICENSE).

## Credits

Based on earlier SubSkip work by drinfernoo. Metadata from [Cinemeta](https://v3-cinemeta.strem.io/manifest.json) and [IntroDB](https://introdb.app/) is subject to those providers' terms. See the included license and attribution. Publication on GitHub does not equal official Kodi repository inclusion.
