# Install IntroSkip

IntroSkip targets **Kodi 22**. The recommended route is to install the small repository ZIP once, then install IntroSkip through Kodi's add-on manager so future versions can update normally.

## Method 1: Download the repository ZIP in a browser

1. Open the [IntroSkip download page](https://zoeywowy.github.io/repository.introskip/) in a normal web browser.
2. Download `repository.introskip-1.0.4.zip`. **Do not extract it.**
3. Make that ZIP accessible to the device running Kodi:
   - **Windows:** leave it in your Downloads folder.
   - **Android / Fire TV:** download it on the device, or copy it to a shared folder/USB storage Kodi can read.
4. In Kodi, open **Add-ons → Install from zip file**.
5. Browse to the folder where the ZIP was downloaded and select `repository.introskip-1.0.4.zip`.
6. Wait for Kodi to confirm that **IntroSkip Repository** was installed.
7. Open **Add-ons → Install from repository → IntroSkip Repository → Services → IntroSkip** and install it.

If the ZIP picker shows only `..` and **0 items**, Kodi is currently inside an empty folder. Go up one level and choose the actual Downloads, USB or shared folder containing the ZIP. The ZIP picker does not download a URL pasted into it.

## Method 2: Add the repository as a File Manager source

If you prefer not to download the ZIP manually:

1. Open **Settings → File manager → Add source**.
2. Enter `https://zoeywowy.github.io/repository.introskip/`.
3. Name the source **IntroSkip Repository** and save it.
4. Open **Add-ons → Install from zip file → IntroSkip Repository**.
5. Select `repository.introskip-1.0.4.zip`.
6. Install IntroSkip from **Install from repository → IntroSkip Repository → Services → IntroSkip**.

The installer is maintained separately at [zoeywowy/repository.introskip](https://github.com/zoeywowy/repository.introskip). It uses Kodi's standard raw GitHub `addons.xml`, matching `addons.xml.md5`, and `datadir zip="true"` layout.

## Method 3: Install the service directly

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
