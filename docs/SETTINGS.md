# IntroSkip settings

Open **Kodi → Add-ons → My add-ons → Services → IntroSkip → Configure**.

## Detection

Choose which segments IntroSkip should look for:

| Option | Default |
| --- | --- |
| Intros | On |
| Recaps | Off |
| Previews | Off |
| TV outros / credits | Off |
| Movie credits | Off |
| Detection notifications | On |

Kodi 22 chapter detection and IntroDB remain available automatically. There is no switch to select one detection source over the other.

## Skip behavior

Choose **Ask** or **Auto** separately for intros, recaps, previews, TV credits and movie credits.

- **Ask** (default): shows a button so you decide whether to skip.
- **Auto**: skips only when the segment passes the safety checks. A named chapter alone is **not** enough for an automatic skip. Film credits are handled conservatively because of possible post-credit scenes.

If you are testing a new video source, start with **Ask**.

## Button appearance

Choose a **Light** or **Dark** theme; each has its own remembered button color. Adjust position, size, style (Pill, Soft or Flat) and content. **Preview button** lets you check the appearance, and **Reset layout** restores the default placement.

## What was removed

Version 0.0.25 no longer includes an Advanced tab, OMDb API key, chapter-inspector button, playback diagnostics action, subtitle detection, or a manual timestamp editor. The public IntroDB snapshot is stored locally and checked against the daily manifest; TheIntroDB API responses are cached for seven days. Neither cache stores a personal viewing history.

If you need help with a missing button or bad timestamps, see [Troubleshooting](TROUBLESHOOTING.md).
