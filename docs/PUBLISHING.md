# Publishing IntroSkip

The Kodi service and its repository feed are separate projects.

- **Service source and release ZIPs:** [service.introskip](https://github.com/zoeywowy/service.introskip)
- **Kodi repository, index and package feed:** [repository.introskip](https://github.com/zoeywowy/repository.introskip)

## Release the service

1. Increment the version in `addon.xml`. Every installable code release needs a new version so Kodi can detect the update.
2. Add a concise entry to `CHANGELOG.md`.
3. Run both offline test suites in separate processes:

   ```bash
   python -m unittest discover -s tests -p 'test_023_integration.py' -v
   python -m unittest discover -s tests -p 'test_023_chapters.py' -v
   ```

4. Build the installable package with `python build_zip.py`.
5. Push the release to `main`. The **Validate and publish IntroSkip pre-release** workflow validates the Python/XML, runs the tests, builds the ZIP and publishes a GitHub pre-release.

The ZIP must contain `service.introskip/addon.xml`, `service.introskip/service.py` and the runtime files under `service.introskip/resources/`.

## Publish the Kodi repository

After the service release is published, open [repository.introskip Actions](https://github.com/zoeywowy/repository.introskip/actions) and run **Build Kodi repository**.

That workflow downloads the service source, builds the Kodi package, generates the repository index and MD5 checksum, publishes the bootstrap ZIP and deploys the GitHub Pages installation page.

## Final checks

Test a fresh Kodi 22 installation and an upgrade over the previous release. Verify title identification, all three detection sources, Ask/Auto behavior, multiple intervals, post-credit protection and button layouts.

IntroSkip is a third-party Kodi add-on, not part of Kodi's official repository.
