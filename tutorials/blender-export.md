# Blender to Walking Mod

Export camera animations from Blender and use them in the Walking Mod. Two export modes: camera motions (handheld feel) and dolly paths (cinematic rails).

## Setup

### Files you need

1. **Blender 3.0+** installed
2. **Export script:** `blender_to_walkingmod_exporter.py` (in the `scripts/` folder of this repo)
3. A Blender scene with an animated camera

### Template scene

Open `rwc_motion_preview.blend` from the mod files. This scene already has:
- A camera at eye height (1.7m)
- A street with buildings and parked cars
- The "Walk to the Store" motion pre-loaded as camera keyframes

Press **Numpad 0** to look through the camera. Press **Space** to play.

## Export a Camera Motion

Camera motions are the handheld shake that overlays on top of your camera in-game. They're relative offsets (small movements around a center point).

### Step by step

1. Open Blender, create or open your scene
2. Select your camera
3. Animate it with the subtle motion you want (keyframe the location and rotation)
4. Open the **Scripting** tab in Blender
5. Paste the export script or open it from file
6. At the bottom of the script, change the function call:

```python
export_camera_to_walking_mod(
    camera_name="YourCameraName",
    output_path=r"C:\path\to\assettocorsa\apps\lua\Realistic Walking Camera\motions\my_motion.json",
    export_type="motion"
)
```

7. Run the script (Alt+P or the play button)
8. The JSON file is created in the motions folder
9. In-game, click **Reload Motions** in the Motion tab

### What to animate

For a handheld feel:
- Move the camera **very slightly** (0.01 to 0.1 meters max)
- Rotate gently (1 to 3 degrees)
- Use smooth keyframe interpolation (Bezier)
- Make it loop: first and last frame should be the same or very close
- 2-5 seconds is a good loop length

For breathing:
- Only animate Y (vertical) with a slow sine wave
- Add very subtle pitch (looking slightly up then down)
- 3-4 second cycle

## Export a Dolly Path

Dolly paths are absolute positions in 3D space. The camera follows a rail through the scene. Use this for cinematic shots.

### Step by step

1. Set up your camera path in Blender (position A to position B, with FOV changes, etc.)
2. Same script, but change `export_type` to `"dolly"`:

```python
export_camera_to_walking_mod(
    camera_name="YourCameraName",
    output_path=r"C:\Users\you\Desktop\my_dolly_track.json",
    export_type="dolly"
)
```

3. Run the script
4. The dolly JSON is saved to your specified path
5. This file can be loaded in the mod's Dolly system (import feature coming soon)

### Coordinate system

Blender and Assetto Corsa use different axes. The export script handles the conversion automatically:

| Blender | Assetto Corsa |
|---------|--------------|
| X (right) | X (right) |
| Y (forward) | Z (forward, negated) |
| Z (up) | Y (up) |

You don't need to worry about this. Just animate naturally in Blender and the script converts.

## Workflow: Create a take in Blender, play in-game

This is the full cinematic workflow:

1. **In Blender:** Place reference objects where cars/buildings are on the AC track
2. **Animate the camera** along the path you want
3. **Export as dolly** using the script
4. **In AC:** Load the Walking Mod, go to the Dolly tab
5. **Import the dolly JSON** (or manually recreate keyframes using K key)
6. **Press P** to play the dolly path

The goal: build a library of camera takes in Blender that you replay in-game.

## Troubleshooting

**Exported JSON is empty** - Make sure the camera has keyframes. Check the camera name matches what you typed in the script.

**Motion looks too strong in-game** - The scale sliders in the Motion tab let you reduce it. Try 0.5 for half intensity.

**Motion doesn't loop smoothly** - Your first and last keyframes need to match. In Blender, copy the first keyframe to the last frame.

**Dolly path is in the wrong position** - The dolly uses absolute world coordinates. Make sure your Blender scene matches the approximate scale of the AC track (1 Blender unit = 1 meter).
