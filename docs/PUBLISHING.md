# Publishing a GitHub release

1. Commit the **repository source** (files at the root, including `addon.xml`), not a GitHub-generated source archive. Make sure the repo README is displayed on the home page.
2. Run the offline tests and `python build_zip.py`. Inspect the ZIP to confirm `service.introskip/addon.xml` is inside.
3. In GitHub, open **Releases → Draft a new release**, tag `v0.0.23`, and title it `IntroSkip v0.0.23 — Kodi 22`.
4. Upload the actual `service.introskip-0.0.23.zip` to **Assets**, not to the source tree. Mark the build a **pre-release** until validated on physical devices.
5. Publish and confirm the asset downloads and installs.
6. For discovery, add repository description and Topics in GitHub **About**: `kodi`, `kodi-addon`, `kodi-22`, `intro-skip`, `credits-skip`, `cinemeta`, `introdb`, `fire-tv`.
7. Enable GitHub Issues for bug reports. To appear in the *official Kodi add-on repository*, follow Kodi's separate add-on submission and review process. A public GitHub repository alone is not enough.
