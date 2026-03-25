# Dolly Camera System

The dolly system lets you create cinematic camera paths with keyframes. Place points A, B, C... and the camera smoothly travels between them.

## Basic Controls

| Key | What it does |
|-----|-------------|
| K | Add keyframe at current camera position |
| Shift+K | Remove last keyframe |
| P | Play/Pause the dolly path |
| R | Reset to beginning |

You need at least 2 keyframes to play a dolly path.

## Quick Start

1. Walk to where you want the shot to start
2. Look in the direction you want
3. Press **K** to save that as keyframe 1
4. Walk to the next position, look where you want
5. Press **K** again for keyframe 2
6. Repeat for as many points as you want
7. Press **P** to play

The camera will smoothly travel from point 1 to 2 to 3 etc., interpolating position, direction, FOV, and roll.

## Dolly Tab Settings

Open the mod's UI and go to the Dolly tab (under Extra/FPS category).

### Keyframe Controls
- **Add Keyframe** - Same as pressing K
- **Remove Last** - Same as Shift+K
- **Clear All** - Removes everything, start fresh

### Playback Settings
- **Duration** - How many seconds the full path takes (1-60s)
- **Speed** - Multiplier (0.5 = half speed, 2.0 = double)
- **Playback Mode:**
  - Once - Play start to end, stop
  - Loop - Repeat forever
  - Ping-Pong - Play forward, then backward, repeat

### Interpolation
- **Linear** - Straight lines between points (robotic)
- **Catmull-Rom** - Smooth curves through all points (recommended)
- **Bezier** - Curves with more control

### Tracking
When enabled, the camera looks at the nearest car while traveling along the path. Good for tracking shots where a car drives by.

## Debug Visualization

Toggle **Show Debug** to see:
- Colored dots at each keyframe position
- Lines connecting the path
- FOV cones showing what each keyframe sees
- Ground markers below each keyframe
- A magenta dot showing current playback position

## Rig Visuals (coming soon)

A new "Rig Visuals" option will add Blender-style gizmos to the dolly view:
- Orange circle gizmos at each keyframe (orbit rings)
- Orange arrow handles showing movement axes
- Crane arm visualization (vertical bar from ground to camera)
- Camera frustum wireframe

This matches exactly what you see in Blender's Dolly Rig and Crane Rig, so the visual language is the same whether you're working in Blender or in-game.

## Tips

- **Start with 3-4 keyframes** for a simple tracking shot. Don't overcomplicate.
- **Use Catmull-Rom interpolation** for smooth curves. Linear looks robotic.
- **Duration matters.** A 10-second dolly at 3 keyframes is smooth. The same path at 2 seconds is frantic.
- **FOV is saved per keyframe.** You can zoom in at point A and zoom out at point B for a dolly zoom effect.
- **Roll is saved too.** Tilt the camera at a keyframe using X+Q/E before pressing K.
- **Tracking + Dolly** is powerful. Set up a straight path, enable tracking, and the camera will follow a passing car while moving along the rail.

## Creating Dolly Paths in Blender

See the [Blender Export tutorial](blender-export.md) for how to animate a camera in Blender and export it as a dolly path for the Walking Mod.
