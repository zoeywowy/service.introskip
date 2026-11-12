# Publishing and release checklist

1. Keep `addon.xml` version, README compatibility notes and CHANGELOG aligned.
2. Run the two test suites separately:
```bash
python -m unittest discover -s tests -p 'test_023_integration.py' -v
python -m unittest discover -s tests -p 'test_023_chapters.py' -v
```
3. Validate `addon.xml`, settings XML and every Python module.
4. Run `python build_zip.py` and inspect the ZIP: top-level directory must be `service.introskip/` containing `addon.xml`.
5. Create a GitHub tag/release such as `v0.0.23`. Attach `service.introskip-0.0.23.zip` as a **release asset**. GitHub-generated source ZIPs are not Kodi installers.
6. Mark as pre-release until tested on real Kodi 22 devices.
7. Add discoverability topics in GitHub About: `kodi`, `kodi-addon`, `kodi-22`, `intro-skip`, `credits-skip`, `cinemeta`, `introdb`, `fire-tv`.

GitHub distribution does not automatically list the add-on in Kodi's official repository. Official inclusion requires Kodi's separate submission/review process.