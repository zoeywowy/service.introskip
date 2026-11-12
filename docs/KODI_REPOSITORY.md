# Kodi repository

The Kodi repository is maintained in its own GitHub project: **[zoeywowy/repository.introskip](https://github.com/zoeywowy/repository.introskip)**.

This service repository contains only the IntroSkip add-on source and its direct-install release ZIP. The separate repository project contains the Kodi repository add-on, generated index, MD5 checksum, and versioned add-on packages.

## Install the repository

1. Open the [IntroSkip download page](https://zoeywowy.github.io/repository.introskip/) in a normal web browser.
2. Download `repository.introskip-1.0.4.zip`. Do not extract it.
3. Make the ZIP accessible to Kodi using Downloads, USB or a shared network folder.
4. In Kodi, choose **Add-ons → Install from zip file** and browse to the downloaded ZIP.
5. Open **Install from repository → IntroSkip Repository → Services → IntroSkip**.

**Do not add the GitHub Pages address as a Kodi File Manager source.** It serves an HTML download page, not a browseable ZIP directory. If the ZIP picker shows only `..` and **0 items**, it is browsing an empty folder; navigate to the folder containing the ZIP.

See the separate project's [installation guide](https://github.com/zoeywowy/repository.introskip/blob/main/docs/INSTALLATION.md) and [maintainer guide](https://github.com/zoeywowy/repository.introskip/blob/main/docs/MAINTAINING.md).

## Direct installation

If you do not want repository-based updates, install the service ZIP from the [IntroSkip Releases page](https://github.com/zoeywowy/service.introskip/releases).

Do not use the old `https://zoeywowy.github.io/service.introskip/` address. That was the previous combined layout and is no longer the repository's installation location.
