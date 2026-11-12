# Contributing

Issues, reproducible bug reports and concise pull requests are welcome.

- Target Kodi 22 rather than introducing compatibility shims for older releases.
- Do not reintroduce subtitle parsing, OMDb/TVDB dependencies, manual timestamps or persistent timestamp caching without an explicit design discussion.
- Preserve the independence of native chapter detection and Cinemeta/IntroDB.
- Reject ambiguous IDs instead of silently selecting an unrelated title.
- Avoid blocking Kodi playback callbacks on network requests.
- Test on Kodi 22 where possible; keep both offline test suites passing.
- Redact streaming URLs, tokens and personal information from logs.

See [the troubleshooting guide](docs/TROUBLESHOOTING.md) for a bug-report template. External service licenses and project attribution should be respected.