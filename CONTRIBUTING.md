# Contributing to IntroSkip

Thanks for helping make IntroSkip better. Start with a [GitHub issue](https://github.com/zoeywowy/service.introskip/issues) and explain the problem, your Kodi build/device and how to reproduce it.

## Development focus

IntroSkip targets **Kodi 22**. Keep changes small and testable, especially around timing, player state and Kodi APIs.

Detection uses **IntroDB** and **named Kodi chapters**; Cinemeta identifies titles for IntroDB. Preserve Ask/Auto safeguards, chapter priority and button customization. Please do not reintroduce subtitle parsing, subtitle caches, OMDb/TVDB keys or persistent cross-episode timestamp caches without a deliberate feature decision.

## Test your changes

```bash
python -m unittest discover -s tests -p 'test_023_integration.py' -v
python -m unittest discover -s tests -p 'test_023_chapters.py' -v
python build_zip.py
python tools/build_kodi_repository.py
```

Run the test suites in separate processes; they use different Kodi stubs. Check XML syntax, ZIP folder structure and, when possible, real Kodi 22 playback.

Do not commit generated `dist/` files, private Kodi settings, personal information, tokens or streaming URLs. Keep existing contributor credits and the [Apache 2.0 license](LICENSE).
