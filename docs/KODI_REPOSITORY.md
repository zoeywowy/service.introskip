# IntroSkip's Kodi repository

The repository bootstrap ZIP is hosted on GitHub Pages. After installation, the repository uses the same standard structure as the A4K repository you supplied: a plain `addons.xml` index, a matching `addons.xml.md5`, and ZIP packages under `addon.id/addon.id-version.zip`.

**Bootstrap download:** [repository.introskip-1.0.3.zip](https://zoeywowy.github.io/service.introskip/repository.introskip-1.0.3.zip)

## Install on Kodi 22

1. Download the bootstrap ZIP to the Kodi device or a location Kodi can access.
2. Open **Add-ons → Install from zip file**.
3. Select `repository.introskip-1.0.3.zip`.
4. Open **Add-ons → Install from repository → IntroSkip Repository → Services → IntroSkip → Install**.

The repository add-on manifest uses these exact Kodi endpoints:

| Purpose | URL |
| --- | --- |
| Add-on index | [addons.xml](https://raw.githubusercontent.com/zoeywowy/service.introskip/main/repository/zips/addons.xml) |
| MD5 checksum | [addons.xml.md5](https://raw.githubusercontent.com/zoeywowy/service.introskip/main/repository/zips/addons.xml.md5) |
| ZIP package base | [repository/zips/](https://github.com/zoeywowy/service.introskip/tree/main/repository/zips) |

The manifest follows the working A4K pattern:

- `<info compressed="false">` points to the raw GitHub XML index.
- `<checksum>` points to the matching raw GitHub MD5 file.
- `<datadir zip="true">` points to the package base directory.
- Each package is stored as `repository/zips/addon.id/addon.id-version.zip`.
- The index and checksum are committed to the same branch as the packages.

GitHub Pages is **not** used for Kodi's update index or package downloads. It only provides the initial repository ZIP download.

## Repository file layout

```text
repository/
└── zips/
    ├── addons.xml
    ├── addons.xml.md5
    ├── repository.introskip/
    │   ├── addon.xml
    │   ├── icon.png
    │   └── repository.introskip-1.0.3.zip
    └── service.introskip/
        ├── addon.xml
        ├── icon.png
        └── service.introskip-0.0.24.zip
```

## Maintainer checks

1. Open [GitHub Pages settings](https://github.com/zoeywowy/service.introskip/settings/pages) and choose **Source: GitHub Actions**.
2. Open [GitHub Actions](https://github.com/zoeywowy/service.introskip/actions) and inspect **Build and deploy Kodi repository to GitHub Pages**.
3. Confirm the workflow validates the XML, exact MD5 digest, `zip="true"` manifest, package folder names and both installable ZIPs.
4. Confirm the public raw GitHub index and checksum URLs load.
5. Test a fresh install and an upgrade on Kodi 22 before declaring success.

The current repository add-on version is **1.0.3**. The IntroSkip service remains **0.0.24**; this repository correction does not change playback or detection code.

See [Publishing](PUBLISHING.md) and [Troubleshooting](TROUBLESHOOTING.md).
