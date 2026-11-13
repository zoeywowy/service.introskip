# IntroSkip settings

Open **Add-ons → My add-ons → Services → IntroSkip → Configure**.

## Detection

Enable the segment types you want IntroSkip to find.

| Setting | Default |
| --- | --- |
| Intros | On |
| Recaps | Off |
| Previews | Off |
| TV credits | Off |
| Movie credits | Off |
| Detection notifications | On |

IntroDB, TheIntroDB and Kodi 22 chapter detection work automatically. There is no source-selection switch.

## Skip behavior

Choose **Ask** or **Auto** separately for each enabled segment type.

- **Ask** (default): display a skip button so you decide.
- **Auto:** automatically seek only when the segment qualifies for the conservative IntroDB safety policy.

TheIntroDB and Kodi chapter matches remain confirmation-only, even when Auto is selected. Movie credits also remain manual unless post-credit information makes the skip boundary safe.

## Button appearance

Choose a **Light** or **Dark** theme. Each theme remembers its own color. You can also change:

- Position: bottom-right, bottom-left, top-right or top-left
- Size: small, normal or large
- Style: Pill, Soft or Flat
- Contents: icon and text, text only or icon only

Use **Preview button** to see the current design. **Reset button appearance** restores the defaults.

For missing buttons or inaccurate timestamps, see [Troubleshooting](TROUBLESHOOTING.md).
