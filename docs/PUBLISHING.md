# Publishing IntroSkip

IntroSkip has two download paths: a **service ZIP** on GitHub Releases and a **Kodi repository** hosted on GitHub Pages. Publishing source code alone does not create either installer.

## Before a release

1. Update the version in the main `addon.xml` and note the changes in `CHANGELOG.md`.
2. Run both offline test suites **in separate processes**:

   ```bash
   python -m unittest discover -s tests -p 'test_023_integration.py' -v
   python -m unittest discover -s tests -p 'test_023_chapters.py' -v
   ```

3. Run `python build_zip.py` and `python tools/build_kodi_repository.py`.
4. Confirm the service ZIP contains `service.introskip/addon.xml` and that `docs/addons.xml` lists the current version. Verify the checksum, repository ZIP and add-on artwork.

## GitHub release

The GitHub workflow **Validate and publish IntroSkip pre-release** tests the build and uploads the Kodi-installable service ZIP under [Releases](https://github.com/zoeywowy/service.introskip/releases). The current workflow is configured for **v0.0.24**. When bumping the version again, update its release number and ZIP references.

The release file must be the ZIP in the **Assets** section. GitHub's automatic “Source code” downloads are not packaged for Kodi.

## Kodi repository and GitHub Pages

The workflow **Build and deploy Kodi repository to GitHub Pages** builds the package directory, index, checksum, artwork and repository installer in `docs/`, commits generated files back to `main`, then publishes the site.

Configure **Settings → Pages → Build and deployment → Source: GitHub Actions**.

**Kodi File Manager source:** `https://zoeywowy.github.io/service.introskip/`

See [Kodi repository setup](KODI_REPOSITORY.md) for the URLs and installation steps. A successful workflow proves its packaging checks passed; verify the published URLs and install on a real Kodi device before declaring success.

## Shipping a stable release

Test a fresh Kodi 22 install and an upgrade from an older version. Verify Cinemeta identification, IntroDB lookups, named chapters, Ask/Auto safety and skip-button layouts on actual playback.

For discoverability, add appropriate GitHub topics and enable [Issues](https://github.com/zoeywowy/service.introskip/issues). Publishing an unofficial repository does **not** submit IntroSkip to Kodi's official add-on repository; that requires a separate review.
