# IntroSkip's Kodi repository

The IntroSkip repository lets you install and update the service from Kodi. GitHub Pages hosts the files, and GitHub Actions prepares them.

**File Manager source:** `https://zoeywowy.github.io/service.introskip/`

## Install from Kodi 22

1. Open **Settings → File manager → Add source**.
2. Enter the source above and name it **IntroSkip**.
3. Go to **Add-ons → Install from zip file → IntroSkip**.
4. Choose `repository.introskip-1.0.1.zip`.
5. Go to **Add-ons → Install from repository → IntroSkip Repository → Services → IntroSkip → Install**.

If Kodi reports **“Could not connect to repository”**, use the [troubleshooting guide](TROUBLESHOOTING.md#repository-wont-connect). Seeing a raw XML document and a browser warning about missing styles is normal.

## Check the published files

| File | What it does |
| --- | --- |
| [Repository installer](https://zoeywowy.github.io/service.introskip/repository.introskip-1.0.1.zip) | Installs IntroSkip Repository |
| [Add-on list](https://zoeywowy.github.io/service.introskip/addons.xml) | Lists available add-ons and their versions |
| [Checksum](https://zoeywowy.github.io/service.introskip/addons.xml.md5) | Signals when the add-on list changes |
| [IntroSkip service ZIP](https://zoeywowy.github.io/service.introskip/service.introskip/service.introskip-0.0.24.zip) | Directly installs the service |
| [Repository homepage](https://zoeywowy.github.io/service.introskip/) | Shows browser download links |

Use **github.io** in Kodi, not the **github.com** source-code address. Kodi looks for packages under `addon.id/addon.id-version.zip`, with the add-on artwork beside the package.

## For maintainers

1. Open [GitHub Pages settings](https://github.com/zoeywowy/service.introskip/settings/pages) and choose **Source: GitHub Actions**.
2. Open [GitHub Actions](https://github.com/zoeywowy/service.introskip/actions) and inspect **Build and deploy Kodi repository to GitHub Pages**.
3. The workflow rebuilds `addons.xml`, its checksum, the repository and service ZIPs and both artwork files.
4. Test the **public** links after deployment, then try the ZIP and repository on a Kodi 22 device.
5. Update the repository add-on version when changing its manifest or connection details. The current repository version is **1.0.1**.

See [Publishing](PUBLISHING.md) for the release process.
