# Contributing

Thanks for helping improve IntroSkip. Before making a change, open a [GitHub issue](https://github.com/zoeywowy/service.introskip/issues) with the problem, Kodi build and steps to reproduce.

## Project scope

IntroSkip targets **Kodi 22 (Piers)** and **Python 3.14**. Keep changes focused, testable and compatible with Kodi's Python runtime.

The detection pipeline consists of:

- Cinemeta for keyless title identification
- IntroDB daily open data, local SQLite lookup and live API fallback
- TheIntroDB v4 as an independent community source
- Kodi 22 native chapter metadata

Preserve chapter priority, multiple intervals, post-credit safeguards, per-segment Ask/Auto behavior and button customization.

Do not reintroduce subtitle parsing, OMDb credentials, Kodi library-ID scraping, playback diagnostics or a second general-purpose timestamp cache without an explicit feature decision. Keep IntroDB's live fallback playback-scoped and retain TheIntroDB's documented seven-day response cache.

## Run the tests

Run the two suites in separate processes because they install different Kodi stubs:

```bash
python -m unittest discover -s tests -p 'test_023_integration.py' -v
python -m unittest discover -s tests -p 'test_023_chapters.py' -v
python build_zip.py
```

The build writes the Kodi-installable service ZIP to `dist/`. The repository feed is built separately in [repository.introskip](https://github.com/zoeywowy/repository.introskip).

## Before submitting

- Validate Python and XML syntax.
- Add or update tests for behavior changes.
- Increment the add-on version for every installable code release.
- Update `CHANGELOG.md` and relevant user documentation.
- Do not commit generated ZIPs, private Kodi settings, credentials, personal information or private streaming URLs.

IntroSkip is licensed under [Apache 2.0](LICENSE).
