# Install IntroSkip

IntroSkip targets **Kodi 22**. Install the repository first if you want Kodi to receive future updates, or install the service ZIP directly.

## Method 1: Install through the Kodi repository

1. Download the [IntroSkip Repository 1.0.3 ZIP](https://zoeywowy.github.io/service.introskip/repository.introskip-1.0.3.zip) to the device running Kodi (or make it available on your network).
2. In Kodi, open **Add-ons → Install from zip file**. If Kodi prompts about unknown sources, enable that option only if you trust this add-on.
3. Select the downloaded `repository.introskip-1.0.3.zip`.
4. Go to **Add-ons → Install from repository → IntroSkip Repository → Services → IntroSkip → Install**.
5. Restart Kodi. To adjust the add-on, open **Add-ons → My add-ons → Services → IntroSkip → Configure**.

The repository installer is hosted on GitHub Pages for the initial install. After installation, Kodi reads the repository index, MD5 checksum and add-on ZIPs from **raw.githubusercontent.com** using Kodi's standard `addons.xml` / `addons.xml.md5` / `datadir zip="true"` layout.

## Method 2: Install the service directly

Use this if you do not need repository-based updates.

1. Download [IntroSkip 0.0.24 ZIP](https://github.com/zoeywowy/service.introskip/releases/download/v0.0.24/service.introskip-0.0.24.zip) from the GitHub release's **Assets**.
2. Make the file accessible to Kodi on your device.
3. Choose **Add-ons → Install from zip file** and select `service.introskip-0.0.24.zip`.
4. Restart Kodi and open IntroSkip's settings.

Do **not** install GitHub's auto-generated “Source code (zip)” file. It is not packaged for Kodi.

Direct installation does not repair or install the repository; it simply installs the service without repository-based updates.

## If installation fails

First confirm your Kodi version. If the repository gives an error, open the [repository troubleshooting steps](TROUBLESHOOTING.md#repository-wont-connect). If the ZIP fails, note the exact error message and look for dependency or XML errors in `kodi.log`. **Do not uninstall your working add-ons or delete your Kodi userdata just to troubleshoot IntroSkip.**

## Update or remove IntroSkip

To update, install a newer package over the existing add-on, or update it through the repository once repository access works. Existing settings are normally kept.

To remove it, open **Add-ons → My add-ons → Services → IntroSkip → Uninstall**. Kodi may separately ask whether to erase settings.

For maintainers: the installable ZIP must contain `service.introskip/addon.xml` and `service.introskip/service.py` inside its top-level `service.introskip/` folder.
