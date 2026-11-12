# Detection architecture

IntroSkip checks two **independent** detection mechanisms during playback:

1. **Kodi 22 chapter detection:** query native `Player.GetChapters` for named recaps, opening credits, title sequences and ending credits. Adjacent named intro chapters can be combined. This does not require Cinemeta or IntroDB.
2. **Cinemeta → IntroDB:** retrieve a playable title, media type and (for television) season/episode from the playing item. Search Cinemeta without an API key to resolve the movie or series IMDb ID. Validate the returned type, title and movie release year where available, then query IntroDB for skip ranges.

The resolver must not blindly accept the top Cinemeta hit: unrelated or ambiguous matches are rejected. IntroDB data takes precedence over heuristic chapters where applicable, with explicit chapter markers treated distinctly.

**Ask vs Auto:** Auto behavior is intentionally conservative. Only qualifying IntroDB matches can trigger auto-skipping; native chapter-only guesses do not automatically jump past content. Ending credits should be handled carefully when post-credit scenes are possible.

**Caching:** Playback-only segment state is temporary; no persistent IMDb-ID or skip timestamp cache is maintained across episodes. Buttons and their graphical resources may be reused.

**Network caveat:** Cinemeta and IntroDB are external services with independent reliability and uptime. Kodi chapters may still work when either provider is unavailable.