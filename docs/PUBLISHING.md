# Publishing IntroSkip

The **service add-on** and the **Kodi repository** are now separate projects.

- Add-on source and direct-install releases: [zoeywowy/service.introskip](https://github.com/zoeywowy/service.introskip)
- Kodi repository installer, index, checksum and package feed: [zoeywowy/repository.introskip](https://github.com/zoeywowy/repository.introskip)

## Before a service release

1. Update the version in the main `addon.xml` and record the changes in `CHANGELOG.md`.
2. Run both offline test suites **in separate processes**:

   ```bash
   python -m unittest discover -s tests -p 'test_023_integration.py' -v
   python -m unittest discover -s tests -p 'test_023_chapters.py' -v
   ```

3. Run `python build_zip.py`.
4. Confirm the ZIP contains `service.introskip/addon.xml`, `service.introskip/service.py`, and the runtime resources under `service.introskip/resources/`.

The **Validate and publish IntroSkip pre-release** workflow tests the code and uploads the installable service ZIP to [GitHub Releases](https://github.com/zoeywowy/service.introskip/releases). Users must download the ZIP from the release's **Assets** section, not GitHub's generated source archive.

## Publish the Kodi repository

The repository is no longer built or hosted from this project. After updating the service version, open [repository.introskip Actions](https://github.com/zoeywowy/repository.introskip/actions) and run **Build Kodi repository**. That workflow checks out this source repository, builds the Kodi ZIP, generates the standard `addons.xml` and `addons.xml.md5` files, and publishes the separate repository feed.

See the repository project's [maintainer guide](https://github.com/zoeywowy/repository.introskip/blob/main/docs/MAINTAINING.md).

## Release testing

Test a fresh Kodi 22 install and an upgrade from an older version. Verify Cinemeta identification, IntroDB lookups, named chapters, Ask/Auto behavior, and skip-button layouts on actual playback.

IntroSkip is an unofficial add-on and is not part of Kodi's official repository.
