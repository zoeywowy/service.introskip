# Installing IntroSkip through Kodi File Manager → Add source

This repository can serve a Kodi-compatible add-on repository using GitHub Pages.

## Step 1: Enable GitHub Pages (repository owner)

Go to **https://github.com/zoeywowy/service.introskip/settings/pages**.

Under **Build and deployment**:

- **Source:** Deploy from a branch
- **Branch:** main
- **Folder:** /docs
- Click **Save**.

When GitHub finishes publishing, verify that the homepage and all URLs below load over HTTPS.

## Step 2: Confirm Kodi repository files

- Kodi File Manager URL: **https://zoeywowy.github.io/service.introskip/**
- Repository installer: **https://zoeywowy.github.io/service.introskip/repository.introskip-1.0.0.zip**
- Kodi add-ons list: **https://zoeywowy.github.io/service.introskip/addons.xml**
- Kodi checksum: **https://zoeywowy.github.io/service.introskip/addons.xml.md5**
- Service ZIP: **https://zoeywowy.github.io/service.introskip/service.introskip/service.introskip-0.0.23.zip**

GitHub Pages is **not active merely because the files exist**; first enable Pages and check the URLs.

## Step 3: Install on Kodi 22 / Firestick

1. Open **Kodi → Settings (gear) → File manager → Add source**.
2. Choose **<None>** and enter **https://zoeywowy.github.io/service.introskip/**.
3. Name the source **IntroSkip** and select **OK**.
4. Return to **Add-ons → Install from zip file**. (If Kodi asks to enable Unknown sources, review the warning and allow it only if you trust this repository.)
5. Open **IntroSkip → repository.introskip-1.0.0.zip** and install it.
6. Return to **Add-ons → Install from repository → IntroSkip Repository**.
7. Open **Services → IntroSkip → Install**.

Once the repository add-on is installed, Kodi can discover updates published to this repository.

## Updating the repository

Updating the project source on GitHub triggers the **Build Kodi repository for GitHub Pages** workflow if changed files match its watched paths. The workflow rebuilds the package, writes the **addons.xml** and checksum, and commits the generated site under **/docs**.

Version updates must match **addon.xml**, and new Kodi release versions should be tested on a real device before broad distribution. If an update did not run, use **Actions → Build Kodi repository for GitHub Pages → Run workflow**.

GitHub's ordinary repository page URL and GitHub Releases page are not Kodi File Manager source addresses; the HTTPS GitHub Pages URL is.
