# Installation

## Prerequisites

- Kodi **22** (the version targeted by this build).
- A device with internet access for Cinemeta and IntroDB lookups.
- Dependencies declared by the add-on: Kodi Python and `script.module.requests`.

## Install

1. Download the asset named `service.introskip-0.0.23.zip` from [GitHub Releases](https://github.com/zoeywowy/service.introskip/releases). **Do not use GitHub's automatically generated Source code ZIP.**
2. Transfer the ZIP onto the Kodi device or make it available to Kodi via a file source.
3. In Kodi: **Settings → Add-ons → Install from zip file**. Enable the required unknown-sources option only if Kodi prompts and you trust the ZIP.
4. Choose the release asset ZIP. After Kodi confirms installation, restart Kodi.
5. Visit **Add-ons → My add-ons → Services → IntroSkip → Configure** to adjust Detection, Skip behavior and Button appearance.

## Upgrade

Install the newest properly rooted release ZIP over the installed version and restart Kodi. Existing preferences should be preserved. Old disabled settings (for example former OMDb key options) may remain in Kodi's userdata but are not used by v0.0.23.

## Uninstall

Use Kodi **My add-ons → Services → IntroSkip → Uninstall**. Kodi may offer to delete user configuration separately.

## Release file layout

The installable ZIP must contain `service.introskip/addon.xml` and `service.introskip/service.py` at its top level. Do **not** rename the internal folder or zip only the contents without the `service.introskip/` prefix.
