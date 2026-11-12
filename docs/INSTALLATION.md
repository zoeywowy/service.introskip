# Install IntroSkip

IntroSkip targets **Kodi 22**. The recommended route is to install the repository ZIP from local storage, then install IntroSkip through Kodi's add-on manager so future versions can update normally.

## Install the repository

1. Open the [IntroSkip download page](https://zoeywowy.github.io/repository.introskip/) in a normal web browser.
2. Click **Download IntroSkip Repository 1.0.4**. Save `repository.introskip-1.0.4.zip`. **Do not extract it.**
3. Make the ZIP accessible to the device running Kodi:
   - **Windows:** leave it in your Downloads folder.
   - **Android / Fire TV:** download it on the device, or copy it to a shared folder/USB storage Kodi can read.
4. In Kodi, open **Add-ons → Install from zip file**.
5. Browse to the local folder containing the ZIP and select `repository.introskip-1.0.4.zip`.
6. Wait for Kodi to confirm that **IntroSkip Repository** was installed.
7. Open **Add-ons → Install from repository → IntroSkip Repository → Services → IntroSkip** and install it.

**Important:** The GitHub Pages address is an HTML download webpage, not a browseable directory. Do not add `https://zoeywowy.github.io/repository.introskip/` as a Kodi File Manager source. Kodi's ZIP picker cannot display the download button from that webpage.

## If the ZIP picker shows an empty folder

If the Install from zip file browser shows only `..` and **0 items**, Kodi is browsing an empty location. Cancel or go up one level, then select the actual Downloads, USB or shared folder where you saved the ZIP. The ZIP picker does not download a URL pasted into it.

## Install the service directly

Use this if you do not need repository-based updates.

1. Download [IntroSkip 0.0.25 ZIP](https://github.com/zoeywowy/service.introskip/releases/download/v0.0.25/service.introskip-0.0.25.zip) from the GitHub release's **Assets**.
2. Make the file accessible to Kodi.
3. Choose **Add-ons → Install from zip file** and select `service.introskip-0.0.25.zip`.
4. Restart Kodi and open IntroSkip's settings.

Do **not** install GitHub's auto-generated “Source code (zip)” file. It is not packaged for Kodi.

Direct installation does not install the repository; it simply installs the service without repository-based updates.

## If installation fails

Confirm your Kodi version and note the exact error. If the repository gives an error, check the [repository project's installation and troubleshooting guide](https://github.com/zoeywowy/repository.introskip/blob/main/docs/INSTALLATION.md). If the service ZIP fails, look for dependency or XML errors in `kodi.log`.

**Do not uninstall your working add-ons or delete your Kodi userdata just to troubleshoot IntroSkip.**

## Update or remove IntroSkip

To update, install a newer package over the existing add-on, or update it through the repository. Existing settings are normally kept.

To remove it, open **Add-ons → My add-ons → Services → IntroSkip → Uninstall**. Kodi may separately ask whether to erase settings.

For maintainers: the installable ZIP must contain `service.introskip/addon.xml` and `service.introskip/service.py` inside its top-level `service.introskip/` folder.
