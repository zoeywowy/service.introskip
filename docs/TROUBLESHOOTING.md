# Troubleshooting and support

## No Skip button
Confirm the title is playing and its Detection option is enabled. If the stream has no recognizable title/season/episode, Cinemeta may not find the right show. Try a title with a known release year or a TV episode with properly exposed season/episode metadata. Some content has no IntroDB segments and no named chapters.

## Cinemeta cannot find an ID
Cinemeta is an external service. A network error, unusual title/translation, incorrect movie year or ambiguous search match can prevent safe identification. IntroSkip deliberately rejects uncertain results instead of using a possibly incorrect IMDb ID. No API key is needed.

## Chapters do not appear
Only Kodi 22 named chapter support is targeted. Some streams have no chapters or only generic chapter numbers. Kodi builds and player/provider integrations may vary.

## Skip buttons are hard to read
Open Button appearance, switch Light/Dark theme and choose its independent color palette. Use the preview. Check button position if a skin overlays controls.

## Buttons skip too far
Try **Ask** instead of **Auto**. Report the show/movie, episode and observed start/end timestamps. Do not assume all credits are safe to skip if post-credit scenes may exist.

## Filing a bug
Use [GitHub Issues](https://github.com/zoeywowy/service.introskip/issues). Include:
- Kodi version/build, OS and device (e.g. Fire TV)
- IntroSkip version
- Streaming add-on/provider, title, season/episode or movie year
- Exact steps to reproduce and expected/actual result
- Relevant **redacted** Kodi log lines

Remove personal tokens, private streaming URLs, credentials, IP addresses and identifying information before uploading logs.