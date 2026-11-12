# Install IntroSkip

IntroSkip targets **Kodi 22**. Install the separate Kodi repository first if you want Kodi to receive future updates, or install the service ZIP directly.

## Method 1: Install through the Kodi repository

1. In Kodi, open **Settings → File manager → Add source**.
2. Enter `https://zoeywowy.github.io/repository.introskip/` and name the source **IntroSkip Repository**.
3. Open **Add-ons → Install from zip file**.
4. Select the **IntroSkip Repository** source, then choose `repository.introskip-1.0.0.zip`.
5. Wait for Kodi to confirm that **IntroSkip Repository** was installed.
6. Open **Add-ons → Install from repository → IntroSkip Repository → Services → IntroSkip** and install it.
7. Restart Kodi if the add-on does not appear immediately.

The repository installer is maintained separately at [zoeywowy/repository.introskip](https://github.com/zoeywowy/repository.introskip). It uses Kodi's standard raw GitHub `addons.xml`, `addons.xml.md5`, and `datadir zip="true"` layout.

## Method 2: Install the service directly

Use this if you do not need repository-based updates.

1. Download [IntroSkip 0.0.24 ZIP](https://github.com/zoeywowy/service.introskip/releases/download/v0.0.24/service.introskip-0.0.24.zip) from the GitHub release's **Assets**.
2. Make the file accessible to Kodi on your device.
3. Choose **Add-ons → Install from zip file** and select `service.introskip-0.0.24.zip`.
4. Restart Kodi and open IntroSkip's settings.

Do **not** install GitHub's auto-generated “Source code (zip)” file. It is not packaged for Kodi.

Direct installation does not install the repository; it simply installs the service without repository-based updates.

## If installation fails

Confirm your Kodi version and note the exact error. If the repository gives an error, check the [repository project's troubleshooting instructions](https://github.com/zoeywowy/repository.introskip/blob/main/docs/INSTALLATION.md). If the service ZIP fails, look for dependency or XML errors in `kodi.log`.

**Do not uninstall your working add-ons or delete your Kodi userdata just to troubleshoot IntroSkip.**

## Update or remove IntroSkip

To update, install a newer package over the existing add-on, or update it through the repository. Existing settings are normally kept.

To remove it, open **Add-ons → My add-ons → Services → IntroSkip → Uninstall**. Kodi may separately ask whether to erase settings.

For maintainers: the installable ZIP must contain `service.introskip/addon.xml` and `service.introskip/service.py` inside its top-level `service.introskip/` folder.
