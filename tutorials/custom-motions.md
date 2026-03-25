# Custom Camera Motions

Camera motions are the subtle handheld shake that makes the camera feel like a real phone or camera. They're simple JSON files.

## What You Get

When you walk in-game, the camera has a natural sway. That sway comes from a motion file. You can create your own and the mod will use it.

## Quick Start

### 1. Create the JSON file

Create a text file with `.json` extension. Here's a minimal example that creates a gentle breathing motion:

```json
{
    "name": "My Breathing Motion",
    "fps": 24,
    "loop": true,
    "type": "walk",
    "frames": [
        {"ox": 0.0, "oy": 0.0, "oz": 0.0, "pitch": 0.0, "yaw": 0.0, "roll": 0.0},
        {"ox": 0.005, "oy": 0.01, "oz": 0.0, "pitch": 0.3, "yaw": 0.0, "roll": 0.1},
        {"ox": 0.01, "oy": 0.02, "oz": 0.005, "pitch": 0.5, "yaw": 0.1, "roll": 0.2},
        {"ox": 0.005, "oy": 0.01, "oz": 0.0, "pitch": 0.3, "yaw": 0.0, "roll": 0.1},
        {"ox": 0.0, "oy": 0.0, "oz": 0.0, "pitch": 0.0, "yaw": 0.0, "roll": 0.0}
    ]
}
```

This creates 5 frames at 24fps that gently move the camera up and tilts slightly, then returns. Because `loop` is true, it repeats forever.

### 2. Drop it in the motions folder

Copy your `.json` file to:
```
assettocorsa/apps/lua/Realistic Walking Camera/motions/
```

### 3. Register it (if auto-scan doesn't work)

Create a file called `custom_motions.txt` in the same `motions/` folder. Put your filename in it, one per line:

```
my_breathing_motion.json
```

### 4. Load in-game

Open the mod's UI, go to the **Motion** tab, and click **Reload Motions**. Your motion will appear in the dropdown.

You can also press **F5** to cycle through loaded motions.

## JSON Reference

### Header

| Field | What it does | Values |
|-------|-------------|--------|
| name | Shows in the UI dropdown | Any text |
| fps | How fast the frames play | 24 or 30 |
| loop | Repeat forever? | true or false |
| type | When the mod uses it automatically | "walk" or "run" |

**About `type`:** If you set it to `"walk"`, the mod uses this motion when you're standing still or walking. If `"run"`, it switches to this motion when you sprint. The mod auto-switches between walk and run motions.

### Frame Fields

Each frame is one snapshot of where the camera should be. The mod interpolates between frames smoothly.

| Field | What it does | Safe range | Unit |
|-------|-------------|-----------|------|
| ox | Move camera left/right | -0.15 to 0.15 | meters |
| oy | Move camera up/down | -0.1 to 0.1 | meters |
| oz | Move camera forward/back | -0.15 to 0.15 | meters |
| pitch | Tilt camera up/down | -5 to 5 | degrees |
| yaw | Pan camera left/right | -3 to 3 | degrees |
| roll | Lean camera sideways | -5 to 5 | degrees |

**Values above these ranges will look exaggerated.** Start small, test in-game, and increase if you want more drama.

## Tips

- **More frames = smoother.** 24fps x 3 seconds = 72 frames. The bundled "Walk to the Store" has ~460 frames.
- **Start and end on the same values** if you want a seamless loop.
- **The motion plays at 50% speed when idle.** So even standing still, there's a gentle breathing effect.
- **Use the Scale sliders** in the Motion tab to adjust intensity without editing the JSON.
- **Validate your JSON** at jsonlint.com before testing. One missing comma will break it.

## What the Bundled Motions Look Like

**Walk to the Store** (type: walk) - Subtle sway like casually walking with a phone. ~19 seconds at 24fps, loops. Position offsets around 0.15m max, rotations around 3-4 degrees.

**Handycam Run** (type: run) - More aggressive shake for running. Faster, more dramatic. Position offsets similar but rotation is heavier.
