# computer-use-grid

English | [中文](README.md)

An engineering solution for **coordinate drift in AI desktop control (computer_use) under high DPI**: **screenshot grid overlay + empirical coordinate calibration + coordinates ledger**.

> Core claim: under high Windows display scaling (125% / 150% / 175% / 200%), screenshots, UIA, and the click API each use a different coordinate system — and won't tell you which. **Any theoretical conversion will be wrong; only empirical calibration self-heals.**

## Features

- 🎯 **Grid overlay**: `overlay-grid.py` overlays a transparent grid onto any computer_use screenshot (major red cells at 100 px / minor white lines at 25 px + ruler numbers). A vision model reads the cell coordinates and obtains "screenshot pixel coordinates" — the same coordinate system as the `coordinate` input, with zero conversion.
- 🧭 **Coordinates ledger**: `coords.json` records **empirically hit** button coordinates per application (only entries verified by the actual landing point + screenshot verification are kept; estimated values are banned). Calibrate once for a given window size, then click directly thereafter.
- 🎯 **Click-aim verification loop**: before clicking — `move_cursor` to preset the real pointer + `get_cursor_position` read-back assertion (P1) → click (P2) → `capture_after` + structural assertion (P3); `diff-aim.py` performs two-frame pixel comparison (AIM_OK / MISS + delta correction advice).
- 🔁 **Fallback**: if the ledger has no entry or the window size changed → relocate via the grid method, then write the calibrated coordinates back to the ledger.
- 🧠 **AX/DOM first**: to judge what a page contains (video? lists? filters?) grep the accessibility tree first; vision is only the fallback (Canvas, AX-less interfaces).
- 🗑️ **Deletion iron rule**: deletion operations go through the context menu + confirmation-dialog detection; exact full-name matching, substring regexes forbidden (a hard lesson from an accidental deletion).

## Installation

```bash
git clone https://github.com/<your-name>/computer-use-grid.git
python3 -m pip install pillow        # dependency (the scripts' only external library)
```

## Usage (three steps)

```bash
# 1. Capture (any computer_use client, e.g. cua-driver / Hermes computer_use)
computer_use capture mode='vision'   # -> screenshot.png

# 2. Overlay the grid
python3 scripts/overlay-grid.py screenshot.png --out screenshot_grid.png

# 3. Let the vision model read the cell -> get target center (x, y) -> click it
computer_use click coordinate=[x, y] capture_after=true
```

### Ledger mode (recommended; no screenshots from the second time on)

```json
{
  "base_size": [1456, 869],
  "coords": {
    "menu_button":     [1191, 25],
    "search_box":      [691, 134],
    "input_field":     [711, 318]
  }
}
```

Look up the ledger → click directly at `coordinate=[x,y]` → hit. When the window size changes once → redo a fallback calibration → write back to the ledger.

## Calibration principle (why it converges)

1. Grid readings and true landing points have a **fixed systematic offset** (produced by DPI × driver viewport coefficients; it differs per window).
2. After the first click, use a `capture_after` screenshot to determine the delta between the landing point and the target.
3. Apply the coordinate correction and retry — **usually a single hit**.
4. Record the corrected, empirically validated coordinates (not the readings) into the ledger — the error is zero from then on. This is "conversion must fail, measurement self-heals".

## Project structure

```text
computer-use-grid/
├── README.md               # Chinese documentation
├── README.en.md            # this file
├── SKILL.md                # methodology handbook (loadable directly as an agent skill)
├── scripts/
│   ├── overlay-grid.py     # grid overlay script (Pillow, single file)
│   └── diff-aim.py         # two-frame pixel comparison: centroid vs target, aim verdict (pure PIL, no extra deps)
├── examples/
│   └── coords.sample.json  # coordinates ledger example (policy & structure)
└── references/
    └── cua-driver-official-skill.md  # archived official cua-driver best practices (for cross-reading)
```

## Known boundaries

- Primarily targeting Windows + high DPI (measured at 2560×1600 @150%); other platforms / scaling factors should be reusable (the workflow is coordinate-system-agnostic) but have not been fully validated.
- The element index path (element_token) is "use if available"; the pixel path is the primary approach — the opposite direction from the official handbook, but empirically more robust where the AX tree is missing or broken.
- On multi-monitor setups or after a DPI change, old ledger entries become invalid and require one re-calibration.

## License

MIT © 2026 yxdgyxlf — see [LICENSE](LICENSE) for details.
