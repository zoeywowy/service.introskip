# Install IntroSkip

IntroSkip targets **Kodi 22**. The recommended method installs the repository once; Kodi can then install and update the service normally.

## Recommended: Kodi repository

1. In Kodi, open **Settings → File manager → Add source**.
2. Enter `https://zoeywowy.github.io/repository.introskip/`.
3. Name the source **IntroSkip Repository** and save it.
4. Open **Add-ons → Install from zip file**.
5. Select **IntroSkip Repository**, then install the repository ZIP Kodi lists.
6. Open **Add-ons → Install from repository → IntroSkip Repository → Services → IntroSkip**.
7. Select **Install**. IntroSkip uses Kodi's built-in Python interface and does not install third-party Python dependencies.

The repository installer is maintained separately. Its [installation guide](https://github.com/zoeywowy/repository.introskip/blob/main/docs/INSTALLATION.md) explains the first-install process and how to troubleshoot the repository source.

## Direct installation

Use this only if you do not want repository-based updates:

1. Open [IntroSkip Releases](https://github.com/zoeywowy/service.introskip/releases).
2. Download the latest `service.introskip-<version>.zip` from the release **Assets**.
3. In Kodi, choose **Add-ons → Install from zip file** and select that ZIP.
4. Restart Kodi if the service does not start immediately.

Do not use GitHub's generated **Source code (zip)** archive; it is not a Kodi install package.

## Update or uninstall

- **Update:** use the IntroSkip Repository's normal add-on update, or install a newer service ZIP over the existing version. Kodi normally preserves your settings.
- **Uninstall:** open **Add-ons → My add-ons → Services → IntroSkip → Uninstall**. Kodi may ask separately whether to remove settings.

Do not delete your Kodi userdata or uninstall unrelated add-ons to troubleshoot IntroSkip.

[Settings](SETTINGS.md) · [Troubleshooting](TROUBLESHOOTING.md)
