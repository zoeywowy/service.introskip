# Kodi repository

The Kodi repository is maintained in its own GitHub project: **[zoeywowy/repository.introskip](https://github.com/zoeywowy/repository.introskip)**.

This service repository contains only the IntroSkip add-on source and its direct-install release ZIP. The separate repository project contains the Kodi repository add-on, generated index, MD5 checksum, and versioned add-on packages.

## Install the repository

1. Open the [IntroSkip download page](https://zoeywowy.github.io/repository.introskip/) in a browser and download `repository.introskip-1.0.4.zip`.
2. In Kodi, choose **Add-ons → Install from zip file** and browse to the downloaded ZIP.
3. Open **Install from repository → IntroSkip Repository → Services → IntroSkip**.

Alternatively, add `https://zoeywowy.github.io/repository.introskip/` as a Kodi **Settings → File manager → Add source** entry, then select that named source in **Install from zip file**.

If Kodi's ZIP picker shows only `..` and **0 items**, it is displaying an empty folder. Navigate to the folder where the ZIP was downloaded or choose the named File Manager source; the ZIP picker itself does not fetch a pasted URL.

See the separate project's [installation guide](https://github.com/zoeywowy/repository.introskip/blob/main/docs/INSTALLATION.md) and [maintainer guide](https://github.com/zoeywowy/repository.introskip/blob/main/docs/MAINTAINING.md).

## Direct installation

If you do not want repository-based updates, install the service ZIP from the [IntroSkip Releases page](https://github.com/zoeywowy/service.introskip/releases).

Do not use the old `https://zoeywowy.github.io/service.introskip/` address. That was the previous combined layout and is no longer the repository's installation location.
