# Soft Clay — a Home Assistant theme

A soft, matte look: a sculpted sage background, cards floating on it with wide
diffuse shadows, terracotta and sage accents, generous rounding.

| Theme | Cards | Background |
|---|---|---|
| `Soft Clay Cream` | cream `#ecebe3` | sage fabric |
| `Soft Clay White` | white `#ffffff` | sage fabric |
| `Soft Clay Dark` | dark `#333d3a` | dark fabric |
| each also as `… (forced)` | same, applied with `!important` | |

The plain variants set Home Assistant's theme variables plus a light `card-mod`
layer for the two things variables cannot do: the backdrop blur behind cards,
and the font. Cards that hard-code their own colours keep them.

The **forced** variants apply the same rules with `!important`, so they take
over those cards too. That is their purpose, at a cost: a card that picks its
text colour to match its own background can become hard to read. Try the plain
edition first.

## Install

1. Copy `themes/Soft Clay/` into `config/themes/`.
2. Copy both files from `www/` into `config/www/`. The themes reference them as
   `/local/clay_bg.svg`.
3. Make sure `configuration.yaml` has:

   ```yaml
   frontend:
     themes: !include_dir_merge_named themes
   ```

4. Run the `frontend.reload_themes` action. No restart needed.
5. Choose it under *Profile → Theme*.

Optional, both degrade gracefully:

- **[card-mod](https://github.com/thomasloven/lovelace-card-mod)** — without it
  the `card-mod-*` keys are ignored; colours, shadows and radii still work, the
  blur and the font do not.
- **Nunito** — add a Lovelace resource of type *stylesheet*, otherwise the
  system sans is used:

  ```
  https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap
  ```

## If a dashboard ignores the theme

A view can carry its own `theme:`, and that beats the profile theme — the
forced variants included, because the chosen theme is never loaded for that
view. Check the view's settings in the dashboard editor.

## Backgrounds

Two SVGs, about 5 KB each: four fabric bands with gradients, drop shadows and a
thin light rim along each crest, plus a noise layer for the weave. They scale
to any screen.

`clay_bg_dark.svg` is generated from `clay_bg.svg` — edit the light one and
re-run the script.

Do not keep copies or backups of theme files under `config/themes/`:
`!include_dir_merge_named` walks subfolders and would load them as duplicates.

## Changing colours

All six files come from `tools/gen_softclay_themes.py`, so the variants stay in
lockstep. Edit `VARIANTS` at the top, then:

```bash
python3 tools/gen_softclay_themes.py --config-dir /path/to/config
```

`--dry-run` reports without writing. Standard library only.

## About the accents

Measured from a reference image, then checked rather than eyeballed:

- Fills use the pale reference tones. Thin marks — strokes, dots, legend chips
  — use a deeper step of the same hue, because the pale sage has a chroma of
  0.036 and 2.4:1 contrast and would read as grey.
- Dark is not an inversion but its own pair, `#c67f4d` and `#3ca694` against
  the `#333d3a` card: ΔE 10.3 under simulated protanopia, 3.5:1 and 3.8:1
  contrast.
- The dark background is darkened until its lightest tone stays below the card
  surface, so cards read as floating panes rather than holes.
- Switches, toggles and sliders are terracotta. Note that today's Home
  Assistant reads `switch-checked-color`; setting only the older
  `switch-checked-button-color` and `-track-color` leaves toggles at the
  default blue. Many themes miss this.

If you change the accents, re-check them against your card colour.

## License

MIT — see [LICENSE](LICENSE).
