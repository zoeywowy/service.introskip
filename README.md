# IntroSkip for Kodi 22

**Automatically find intros, recaps and credits with Cinemeta, IntroDB and Kodi's native chapters.**

![Kodi 22](https://img.shields.io/badge/Kodi-22-blue) ![Python 3](https://img.shields.io/badge/Python-3-blue) ![Release](https://img.shields.io/badge/release-v0.0.23-orange) ![License](https://img.shields.io/badge/license-Apache--2.0-green)

IntroSkip is a lightweight Kodi service add-on for TV episodes and movies. When a supported segment is detected, it displays a remote-friendly **Skip Intro**, **Skip Recap**, or **Skip Credits** button. Skip behavior can be set to **Ask** or **Auto**; automatic skipping only uses eligible IntroDB timestamps, not unverified chapter guesses.

> **Release status:** v0.0.23 is a **pre-release candidate**. Offline tests pass, but real-world Kodi 22/Fire TV playback testing is still needed. Please report problems under [Issues](https://github.com/zoeywowy/service.introskip/issues).

## Download and install

1. Open the [Releases page](https://github.com/zoeywowy/service.introskip/releases).
2. Download **`service.introskip-0.0.23.zip` from the release Assets** (not GitHub's automatic “Source code” archive).
3. On Kodi 22, open **Add-ons → Install from zip file**, browse to the ZIP and install it.
4. Restart Kodi after upgrading. Configure **Detection**, **Skip behavior**, and **Button appearance** in IntroSkip's settings.

> A release asset will appear on the Releases page once it is uploaded. Publishing source code alone does not create a Kodi-installable asset.

[Detailed installation guide](docs/INSTALLATION.md) · [How detection works](docs/DETECTION.md) · [Settings](docs/SETTINGS.md) · [Troubleshooting](docs/TROUBLESHOOTING.md)

## Features

- **Zero API keys:** searches the public Cinemeta JSON API for IMDb title IDs; no Stremio installation is necessary.
- **TV and movies:** searches series by show title and movies by title/year where known. Series IDs are combined with season/episode for IntroDB.
- **IntroDB:** retrieves community-submitted segment timestamps without storing a persistent timestamp cache.
- **Kodi 22 chapters:** reads explicitly named chapters independently of the network, including adjacent intro markers and end-credit markers.
- **Safe prompting:** configurable Ask/Auto settings, with conservative handling of chapter-only and post-credit segments.
- **Button customization:** independent Light/Dark color choices, styles, sizes, on-screen position and preview.
- **Simplified interface:** no API-key setup, subtitle scraping, diagnostic tools, or manual timestamp editor.

## Compatibility

**Developed for Kodi 22** with Python 3; targeted particularly at Android/Fire TV. Actual compatibility varies by Kodi build, skin and provider. Kodi 21 and older are not the target. Requires Kodi's `xbmc.python` and `script.module.requests` modules (declared in `addon.xml`).

## How it works

```text
Playback title + media type + season/episode (provided by playing item)
  |-- Independent Kodi 22 named chapter detection
  `-- Cinemeta title search -> verified IMDb ID -> IntroDB timestamps
                                      |
                          Skip segments + source priority
                                      |
                            On-screen skip button
```

Cinemeta is **not** a Kodi add-on. It is a separate public metadata service accessed over HTTPS. Kodi still supplies the basic title and episode information. A strict match policy rejects ambiguous or unrelated search results, rather than trusting the first/highest-ranked result. If Cinemeta or IntroDB is unavailable, chapter detection may still work.

## Privacy

The add-on contacts **Cinemeta** and **IntroDB** over HTTPS as needed for identification and skip segments. It does not read subtitle files, store API keys or save IMDb IDs/skip timestamps in a persistent database. Its current playback memory is cleared when playback changes. Kodi logs may contain diagnostic text about title and lookup status.

## Development and testing

Source code lives at repository root (`addon.xml`, `service.py`, `main.py`, `resources/`). Tests are in `tests/`. Run the two offline suites in separate Python processes because each provides its own Kodi stubs:

```bash
python -m unittest discover -s tests -p 'test_023_integration.py' -v
python -m unittest discover -s tests -p 'test_023_chapters.py' -v
```

Use `python build_zip.py` to produce a properly rooted Kodi installation ZIP under `dist/`. The `dist` directory is intentionally not committed to source control.

## Releases and feedback

See [Changelog](CHANGELOG.md), [support and issue reporting](docs/TROUBLESHOOTING.md), and [contribution guide](CONTRIBUTING.md). Source updates on GitHub are not the same as inclusion in Kodi's official add-on repository; that requires a separate submission/review.

## Credits and licensing

Based on earlier **SubSkip** work by **drinfernoo**. Metadata services: [Cinemeta](https://v3-cinemeta.strem.io/manifest.json) and [IntroDB](https://introdb.app/). IntroSkip code is presented under **Apache License 2.0**; see [LICENSE](LICENSE). External services and dependencies have their own terms.
