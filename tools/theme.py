"""Two palettes: 'light' (day, macaron pastels) and 'dark' (night, midnight neon).

Every component is generated once per theme; README.md picks the right one
with <picture> + prefers-color-scheme.
"""

LIGHT = {
    "name": "light",
    # ui chrome
    "panel": "#FFFDF8",
    "panel2": "#FBF4EE",
    "well": "#F5EDF4",
    "frame": "#2A2140",
    "hilite": "#FFFFFF",
    "shadow": "#D5CAE4",
    "line": "#E6DCEA",
    "track": "#EDE5F0",
    "radar": "#E9E0F7",
    "chip_line": "#CFC3DF",
    # text
    "text": "#2A2140",
    "text2": "#5E5575",
    "text3": "#9A90B0",
    # accents: (fill, ink)
    "pink": ("#F2B8C6", "#CF6F8E"),
    "lav": ("#BBA9E0", "#7A62B0"),
    "blue": ("#AEB9DB", "#5D6EAE"),
    "teal": ("#9FD4D1", "#3A9893"),
    "peach": ("#F6D6A8", "#BF8331"),
    "coral": ("#F4A48C", "#CF6247"),
    "gold": ("#FFD66B", "#B98713"),
}

DARK = {
    "name": "dark",
    "panel": "#1B1734",
    "panel2": "#221D40",
    "well": "#15122A",
    "frame": "#5C4E9E",
    "hilite": "#3A3170",
    "shadow": "#06050F",
    "line": "#2E2757",
    "track": "#2A2450",
    "radar": "#342A68",
    "chip_line": "#3A3270",
    "text": "#F4EEFF",
    "text2": "#BDB3DC",
    "text3": "#8177A8",
    "pink": ("#F59BBB", "#F7B6CC"),
    "lav": ("#A68CEB", "#C4B0F6"),
    "blue": ("#8EA2F0", "#B2C0F7"),
    "teal": ("#52CEC3", "#86E3DA"),
    "peach": ("#FFC978", "#FFD9A0"),
    "coral": ("#FF8F72", "#FFAD97"),
    "gold": ("#FFD66B", "#FFE08F"),
}

THEMES = [LIGHT, DARK]
