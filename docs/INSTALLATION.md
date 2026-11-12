# Install IntroSkip

IntroSkip targets **Kodi 22**. You can install it through its repository (which is intended to provide updates) or install the service directly from a ZIP.

## Method 1: Install through the Kodi repository

1. Open **Kodi → Settings (gear) → File manager → Add source**.
2. Select **<None>**, enter the source address below, then name it **IntroSkip**.

   `https://zoeywowy.github.io/service.introskip/`

3. Go to **Add-ons → Install from zip file**. If Kodi prompts about unknown sources, enable that option only if you trust this add-on.
4. Select **IntroSkip**, then `repository.introskip-1.0.0.zip`.
5. Go to **Add-ons → Install from repository → IntroSkip Repository → Services → IntroSkip → Install**.
6. Restart Kodi. To adjust the add-on, open **Add-ons → My add-ons → Services → IntroSkip → Configure**.

The **github.com** project URL is for source code. The **github.io** URL above is the Kodi File Manager source.

## Method 2: Install the service directly

Use this if you do not need repository-based updates or if Kodi displays **“Could not connect to repository.”**

1. Download [IntroSkip 0.0.23 ZIP](https://github.com/zoeywowy/service.introskip/releases/download/v0.0.23/service.introskip-0.0.23.zip) from the GitHub release's **Assets**.
2. Make the file accessible to Kodi on your device.
3. Choose **Add-ons → Install from zip file** and select `service.introskip-0.0.23.zip`.
4. Restart Kodi and open IntroSkip's settings.

Do **not** install GitHub's auto-generated “Source code (zip)” file. It is not packaged for Kodi.

Direct installation does not repair a broken repository; it simply lets you try the add-on without that download path.

## If installation fails

First confirm your Kodi version. If the repository gives an error, open the [repository troubleshooting steps](TROUBLESHOOTING.md#repository-wont-connect). If the ZIP fails, note the exact error message and look for dependency or XML errors in `kodi.log`. **Do not uninstall your working add-ons or delete your Kodi userdata just to troubleshoot IntroSkip.**

## Update or remove IntroSkip

To update, install a newer package over the existing add-on, or update it through the repository once repository access works. Existing settings are normally kept. Older unused preferences may remain in Kodi's profile, but 0.0.23 does not use them.

To remove it, open **Add-ons → My add-ons → Services → IntroSkip → Uninstall**. Kodi may separately ask whether to erase settings.

For maintainers: the installable ZIP must contain `service.introskip/addon.xml` and `service.introskip/service.py` inside its top-level `service.introskip/` folder.
