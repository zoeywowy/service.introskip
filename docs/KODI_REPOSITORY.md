# Installing IntroSkip through Kodi File Manager → Add source

This repository publishes a Kodi-compatible add-on repository using **GitHub Pages and GitHub Actions**.

## Step 1: Confirm GitHub Pages is configured

Open **https://github.com/zoeywowy/service.introskip/settings/pages**.

Under **Build and deployment**:

- Set **Source** to **GitHub Actions**.
- The workflow `.github/workflows/kodi-repository.yml` builds the Kodi repository and deploys the `docs/` site automatically.
- Do not select **Deploy from a branch** for this workflow.

The latest deployment can be checked under **Actions → Build and deploy Kodi repository to GitHub Pages**. A successful run means GitHub accepted the Pages deployment; it does not test connectivity from an individual Kodi device.

## Step 2: Verify the published repository files

- Kodi File Manager source: **https://zoeywowy.github.io/service.introskip/**
- Repository installer: **https://zoeywowy.github.io/service.introskip/repository.introskip-1.0.0.zip**
- Kodi add-ons list: **https://zoeywowy.github.io/service.introskip/addons.xml**
- Kodi checksum: **https://zoeywowy.github.io/service.introskip/addons.xml.md5**
- Direct IntroSkip package: **https://zoeywowy.github.io/service.introskip/service.introskip/service.introskip-0.0.23.zip**

The GitHub repository page (**github.com/zoeywowy/service.introskip**) is the source-code page, not the Kodi File Manager source. Use the **github.io** address above.

Before installing, open the `addons.xml` link in a browser. It should display XML beginning with an `<addons>` root element, not a GitHub 404 page or an HTML error page.

## Step 3: Install on Kodi 22 / Fire TV

1. Open **Kodi → Settings (gear) → File manager → Add source**.
2. Choose **<None>** and enter **https://zoeywowy.github.io/service.introskip/**.
3. Name the source **IntroSkip** and select **OK**.
4. Return to **Add-ons → Install from zip file**. If Kodi asks to enable Unknown sources, review the warning and allow it only if you trust this repository.
5. Open the **IntroSkip** source and install **repository.introskip-1.0.0.zip**.
6. Return to **Add-ons → Install from repository → IntroSkip Repository**.
7. Open **Services → IntroSkip → Install**.

Once installed, Kodi can discover updates published to this repository.

## Troubleshooting “Could not connect to repository”

1. Open **https://zoeywowy.github.io/service.introskip/addons.xml** in a browser on the same network as Kodi.
2. If it does not load as XML, Kodi cannot retrieve the repository index either. Check the Pages deployment and network/DNS access.
3. If it does load as XML, restart Kodi and try opening **IntroSkip Repository** again.
4. If the error remains, capture the Kodi log immediately after reproducing it. The useful lines include `repository.introskip`, `addons.xml`, `CCurlFile`, and `GetDirectory`; they show whether Kodi failed on the index, checksum, or network request.

## Updating the repository

Pushing changes to watched source files on `main` triggers the **Build and deploy Kodi repository to GitHub Pages** workflow. It rebuilds the installable ZIP, writes `addons.xml` and its checksum, commits generated repository files under `docs/`, and deploys the site.

To publish manually, open **Actions → Build and deploy Kodi repository to GitHub Pages → Run workflow**. Version updates must match the source `addon.xml`. Test new Kodi builds on a real device before broad distribution.

GitHub's ordinary repository page and GitHub Releases page are not Kodi File Manager source addresses; the HTTPS GitHub Pages URL is.
