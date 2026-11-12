# Installing IntroSkip v0.0.23

**Requirements:** Kodi 22, Python 3 support, and an internet connection for Cinemeta and IntroDB lookups. Named Kodi chapters can work without the network.

1. Open the project's [GitHub Releases](https://github.com/zoeywowy/service.introskip/releases).
2. Under a release's **Assets**, download the file named `service.introskip-0.0.23.zip` (not the automatically generated **Source code** ZIP).
3. In Kodi choose **Settings → Add-ons → Install from zip file**. Allow the source when Kodi requests confirmation.
4. Select the ZIP. Kodi will install the declared requests dependency if it is available.
5. Restart Kodi and open **Add-ons → My add-ons → Services → IntroSkip → Configure**.
6. Review Detection, Skip behavior and Button appearance.

**Upgrade:** Install the newer ZIP over your old IntroSkip version, then restart Kodi. If settings look inconsistent, revisit the appearance selectors.

**Not seeing a release asset?** The source files alone are not the installable ZIP; wait until an asset is attached or build it locally from the complete source using `python build_zip.py`.

**Testing:** Try a TV episode with a recognizable series title/season/episode and a movie with a clear title and year. For issues, see [Troubleshooting](TROUBLESHOOTING.md).