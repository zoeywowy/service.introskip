# Contributing

Thanks for helping improve IntroSkip. Before making changes, open an [issue](https://github.com/zoeywowy/service.introskip/issues) describing the problem or proposed improvement. Please include the Kodi version, player/provider and reproduction steps when relevant.

Keep changes focused on Kodi 22. Don't reintroduce subtitle parsing, persistent timestamp/IMDb caches, TVDB/OMDb API-key dependencies or manual timestamp maintenance without an explicit feature decision. Preserve the Ask/Auto safety behavior and named-chapter priority. Do not commit secrets, personal data, video stream URLs, Kodi user settings, or generated ZIP artifacts.

Run `python -m unittest discover -s tests -p 'test_023_integration.py' -v` and `python -m unittest discover -s tests -p 'test_023_chapters.py' -v` and check XML/ZIP integrity before proposing changes. Contributions should retain existing attribution and Apache-2.0 notices.
