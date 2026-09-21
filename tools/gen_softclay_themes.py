#!/usr/bin/env python3
"""Generate the six "Soft Clay" themes into <config>/themes/Soft Clay/.

One source for all six so the variants cannot drift apart:

    Soft Clay Cream / White / Dark              plain
    Soft Clay Cream / White / Dark (forced)     same, with !important

The plain variants set Home Assistant's theme variables and add a light
card-mod layer for the two things variables cannot do: the backdrop blur
behind cards, and the font. Cards that hard-code their own colours are left
alone.

The forced variants apply the same rules with !important, so they also take
over such cards. That is the point of them, at a cost: a card that picks its
text colour to match its own background can become hard to read.

A view with its own `theme:` beats the theme from the user profile - the
forced variants included, since that theme is never loaded for the view.
`--report` lists views that do this.

    python3 gen_softclay_themes.py --report
    python3 gen_softclay_themes.py --config-dir /path/to/config
    python3 gen_softclay_themes.py --dry-run
    python3 gen_softclay_themes.py
"""
import os, re, sys

CONFIG_DIR = "/config"
FONT = "Nunito, 'Segoe UI', Roboto, system-ui, sans-serif"
BG_LIGHT = "/local/clay_bg.svg"
BG_DARK = "/local/clay_bg_dark.svg"
RADIUS = "24px"
BLUR = "blur(14px) saturate(1.05)"


def out_dir():
    return os.path.join(CONFIG_DIR, "themes", "Soft Clay")


def bg_path(name):
    return os.path.join(CONFIG_DIR, "www", name)


def theme_name(key, forced):
    return f"Soft Clay {key}" + (" (forced)" if forced else "")


# Accents are measured and checked, not guessed. Cream and White share
# #c17842 / #2c9a88: against both surfaces they clear the lightness band, the
# chroma floor, colour-vision separation (dE 9.5 protan) and the normal-vision
# floor (dE 19.1). Dark gets its own steps rather than an inversion: #c67f4d
# and #3ca694 against the #333d3a card, dE 10.3, 3.5:1 and 3.8:1 contrast.
# Re-check any change against the card colour instead of trusting the eye.
VARIANTS = {
    "Cream": dict(
        page="#8ca09b", page2="#9cafa9", bg=BG_LIGHT,
        card="#ecebe3", card_a="rgba(236, 235, 227, 0.84)",
        ink="#3c4642", muted="#616d68", divider="#dcdbd1", field="#e3e2d8",
        idle_line="#c3c2b5",
        primary="#c17842", accent="#2c9a88",
        header="#7c8d89", header_ink="#f2f4ef",
        shadow=("0 20px 44px rgba(45, 58, 54, 0.20), 0 6px 14px rgba(45, 58, 54, 0.10), "
                "inset 0 1px 0 rgba(255, 255, 255, 0.85)"),
        comment="Cream cards on the sage background."),
    "White": dict(
        page="#8ca09b", page2="#9cafa9", bg=BG_LIGHT,
        card="#ffffff", card_a="rgba(255, 255, 255, 0.90)",
        ink="#2f3835", muted="#5c6864", divider="#e4e6e2", field="#f1f3f0",
        idle_line="#c9cdc8",
        primary="#c17842", accent="#2c9a88",
        header="#7c8d89", header_ink="#ffffff",
        shadow=("0 20px 44px rgba(45, 58, 54, 0.22), 0 6px 14px rgba(45, 58, 54, 0.12), "
                "inset 0 1px 0 rgba(255, 255, 255, 0.95)"),
        comment="White cards, same accents as Cream."),
    "Dark": dict(
        page="#232b29", page2="#2b3330", bg=BG_DARK,
        card="#333d3a", card_a="rgba(51, 61, 58, 0.86)",
        ink="#e9ede9", muted="#adb9b4", divider="#46524e", field="#3c4744",
        idle_line="#5a6662",
        primary="#c67f4d", accent="#3ca694",
        header="#28302e", header_ink="#e9ede9",
        shadow=("0 22px 48px rgba(10, 16, 14, 0.52), 0 6px 14px rgba(10, 16, 14, 0.34), "
                "inset 0 1px 0 rgba(255, 255, 255, 0.10)"),
        comment="Dark cards on the dark background, with their own checked accents."),
}


def mix(a, b, t):
    pa = [int(a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    pb = [int(b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(pa, pb))


def tokens(v):
    """Home Assistant's theme variables. Covers the built-in cards."""
    return {
        "primary-background-color": v["page"],
        "secondary-background-color": v["page2"],
        "lovelace-background": f"center / cover no-repeat fixed url('{v['bg']}'), {v['page']}",
        "card-background-color": v["card"],
        "ha-card-background": v["card_a"],
        "ha-card-border-width": "0",
        "ha-card-border-radius": RADIUS,
        "ha-card-box-shadow": v["shadow"],
        "primary-text-color": v["ink"],
        "secondary-text-color": v["muted"],
        "text-primary-color": v["ink"],
        "disabled-text-color": v["muted"],
        "primary-color": v["primary"],
        "accent-color": v["accent"],
        "divider-color": v["divider"],
        "app-header-background-color": v["header"],
        "app-header-text-color": v["header_ink"],
        "app-header-selection-bar-color": v["primary"],
        "sidebar-background-color": v["card"],
        "sidebar-icon-color": v["muted"],
        "sidebar-text-color": v["ink"],
        "sidebar-selected-icon-color": v["primary"],
        "sidebar-selected-text-color": v["ink"],
        "state-icon-color": v["muted"],
        "state-icon-active-color": v["primary"],
        "paper-item-icon-color": v["muted"],
        "paper-item-icon-active-color": v["primary"],
        # switch-checked-color is the key that matters: today's ha-switch reads
        # it. Setting only the older button/track names leaves toggles at the
        # default blue - a common miss.
        "switch-checked-color": v["primary"],
        "switch-checked-button-color": v["primary"],
        "switch-checked-track-color": mix(v["primary"], "#ffffff", 0.45),
        "switch-unchecked-button-color": v["muted"],
        "switch-unchecked-track-color": v["divider"],
        "paper-toggle-button-checked-button-color": v["primary"],
        "paper-toggle-button-checked-bar-color": mix(v["primary"], "#ffffff", 0.45),
        "paper-toggle-button-unchecked-button-color": v["muted"],
        "paper-toggle-button-unchecked-bar-color": v["divider"],
        "slider-color": v["primary"],
        "slider-bar-color": v["divider"],
        "paper-slider-knob-color": v["primary"],
        "paper-slider-knob-start-color": v["primary"],
        "paper-slider-active-color": v["primary"],
        "paper-slider-secondary-color": mix(v["primary"], "#ffffff", 0.45),
        "paper-slider-container-color": v["divider"],
        "input-fill-color": v["field"],
        "input-ink-color": v["ink"],
        "input-label-ink-color": v["muted"],
        "input-idle-line-color": v["idle_line"],
        "input-hover-line-color": v["primary"],
        "mdc-theme-primary": v["primary"],
        "ha-dialog-surface-background": v["card"],
        "dialog-box-shadow": v["shadow"],
        "history-unknown-color": v["divider"],
        "state-unavailable-color": v["divider"],
        # Nunito has to be loaded as a Lovelace resource; without it the system
        # sans is used.
        "primary-font-family": FONT,
        "paper-font-common-base_-_font-family": FONT,
        "paper-font-body1_-_font-family": FONT,
        "paper-font-headline_-_font-family": FONT,
        "ha-card-header-font-family": FONT,
    }


def card_css(v, forced):
    i = " !important" if forced else ""
    css = ["ha-card {"]
    if forced:
        css += [f"  background: {v['card_a']}{i};",
                f"  color: {v['ink']}{i};",
                f"  border: none{i};",
                f"  border-radius: {RADIUS}{i};",
                f"  box-shadow: {v['shadow']}{i};"]
    css += [f"  backdrop-filter: {BLUR}{i};",
            f"  -webkit-backdrop-filter: {BLUR}{i};",
            f"  font-family: {FONT}{i};",
            "}"]
    if forced:
        css += ["ha-card * {", f"  font-family: inherit{i};", "}"]
    # No rule against nested cards on purpose: card-mod injects its CSS into
    # each card's own shadow root, and a selector like "ha-card ha-card" does
    # not reach across that boundary. Such a rule would look right and do
    # nothing. If one card stacks shadow on shadow, put the exception on that
    # card via its own card_mod.
    return "\n".join(css) + "\n"


def root_css(forced):
    i = " !important" if forced else ""
    return ".header, ha-app-layout {\n" f"  font-family: {FONT}{i};\n" "}\n"


def yaml_block(name, v, forced):
    lines = [f"# {name} - {v['comment']}"]
    if forced:
        lines.append("# Forced: wins over cards that bring their own colours.")
    lines.append("# Generated by gen_softclay_themes.py - edit that, not this file.")
    lines.append(f"{name}:")
    lines.append(f"  card-mod-theme: '{name}'")
    for k, val in tokens(v).items():
        lines.append(f'  {k}: "{val}"')
    for key, css in (("card-mod-card", card_css(v, forced)),
                     ("card-mod-root", root_css(forced))):
        lines.append(f"  {key}: |")
        lines += [f"    {ln}" if ln else "" for ln in css.rstrip("\n").split("\n")]
    return "\n".join(lines) + "\n"


# --- dark background, derived from the light one -----------------------------
M1 = [[1, 0.3963377774, 0.2158037573], [1, -0.1055613458, -0.0638541728],
      [1, -0.0894841775, -1.2914855480]]
M2 = [[4.0767416621, -3.3077115913, 0.2309699292],
      [-1.2684380046, 2.6097574011, -0.3413193965],
      [-0.0041960863, -0.7034186147, 1.7076147010]]


def _s2lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lin2s(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def darken(hexcol, factor=0.26, floor=0.05):
    """Compress lightness in OKLab, keeping hue and chroma - a plain RGB
    multiply would desaturate the tones.

    The values keep the background's lightest tone (L 0.30) below the dark card
    surface #333d3a (L 0.35). Otherwise the fabric would be lighter than the
    cards in places and they would read as holes rather than floating panes."""
    h = hexcol.lstrip("#")
    r, g, b = (_s2lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    L = floor + L * factor
    lms = [(row[0] * L + row[1] * A + row[2] * B) ** 3 for row in M1]
    rgb = [sum(M2[i][j] * lms[j] for j in range(3)) for i in range(3)]
    return "#" + "".join(f"{round(_lin2s(c) * 255):02x}" for c in rgb)


def write_dark_background(dry):
    src = open(bg_path("clay_bg.svg")).read()
    out = re.sub(r'#[0-9a-fA-F]{6}', lambda m: darken(m.group(0)), src)
    out = re.sub(r'(?s)<!--.*?-->',
                 "<!-- Dark edition of the Soft Clay background. Generated by "
                 "gen_softclay_themes.py from clay_bg.svg - edit that one. -->",
                 out, count=1)
    dest = bg_path("clay_bg_dark.svg")
    if not dry:
        open(dest, "w").write(out)
    return dest


# --- optional: talk to a running Home Assistant ------------------------------
def report():
    """List views that carry their own theme; those ignore the profile theme."""
    import ha_ws
    for d in ha_ws.call({"type": "lovelace/dashboards/list"}) + [{"url_path": None}]:
        try:
            cfg = ha_ws.load_dashboard(d["url_path"])
        except RuntimeError:
            continue
        for v in cfg.get("views", []):
            if v.get("theme"):
                print(f"    {str(d.get('url_path') or 'lovelace'):24s} "
                      f"{v.get('title', v.get('path', '?')):16s} -> {v['theme']}")


def clear_view_themes(url_path, dry):
    """Drop `theme:` from every view of a dashboard, with a backup first.

    On a dashboard built by a script this does not last: the next run puts the
    view theme back. There the change belongs in that script."""
    import datetime, json
    import ha_ws
    cfg = ha_ws.load_dashboard(url_path)
    hits = [v for v in cfg.get("views", []) if v.get("theme")]
    if not hits:
        print(f"  {url_path or 'lovelace'}: no view carries its own theme")
        return
    for v in hits:
        print(f"  {url_path or 'lovelace'}: \"{v.get('title', v.get('path', '?'))}\" "
              f"loses theme {v['theme']}")
    if dry:
        print("  --dry-run: nothing written")
        return
    stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    dest = os.path.join(CONFIG_DIR, ".storage",
                        f"lovelace.{(url_path or 'lovelace').replace('-', '_')}.bak-{stamp}")
    json.dump({"data": {"config": cfg}}, open(dest, "w"), ensure_ascii=False, indent=1)
    print(f"  backup: {dest}")
    for v in hits:
        v.pop("theme")
    ha_ws.save_dashboard(url_path, cfg)


def main():
    global CONFIG_DIR
    dry = "--dry-run" in sys.argv
    if "--config-dir" in sys.argv:
        CONFIG_DIR = sys.argv[sys.argv.index("--config-dir") + 1]
    if "--report" in sys.argv:
        report()
        return
    if "--clear-view-themes" in sys.argv:
        rest = [a for a in sys.argv[sys.argv.index("--clear-view-themes") + 1:]
                if not a.startswith("--")]
        if not rest:
            print("  name a dashboard, e.g. --clear-view-themes lovelace")
            return
        clear_view_themes(None if rest[0] == "lovelace" else rest[0], dry)
        return
    print(f"  {write_dark_background(dry)} " + ("would be written" if dry else "written"))
    if not dry:
        os.makedirs(out_dir(), exist_ok=True)
    for key, v in VARIANTS.items():
        for forced in (False, True):
            name = theme_name(key, forced)
            path = os.path.join(out_dir(), name.replace(" ", "_") + ".yaml")
            text = yaml_block(name, v, forced)
            if not dry:
                open(path, "w").write(text)
            print(f"  {name:28s} {len(text.splitlines()):3d} lines  {path}")
    if dry:
        print("  --dry-run: nothing written")
        return
    print("  reload with the frontend.reload_themes action")


if __name__ == "__main__":
    main()
