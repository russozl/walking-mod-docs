# Custom Characters

Add your own 3D character models and animations to the Walking Mod.

This is the most involved customization. You need Blender and the KS Editor.

## Requirements

- [Blender](https://www.blender.org/) 3.0+
- [KS Editor](https://www.assettocorsa.net/forum/) (comes with AC SDK)
- A character model (FBX from Mixamo, or your own)

## Adding a Character Model

### 1. Get a character

Go to [mixamo.com](https://www.mixamo.com), pick a character, download as FBX in T-Pose.

Or use any humanoid FBX model.

### 2. Prepare bones in Blender

The Walking Mod expects specific bone names. Your model's skeleton must use this naming:

```
DRIVER:RIG_Hips
DRIVER:RIG_Spine
DRIVER:RIG_Spine1
DRIVER:RIG_Spine2
DRIVER:RIG_Neck
DRIVER:RIG_Head
DRIVER:RIG_LeftUpLeg
DRIVER:RIG_LeftLeg
DRIVER:RIG_LeftFoot
DRIVER:RIG_RightUpLeg
DRIVER:RIG_RightLeg
DRIVER:RIG_RightFoot
DRIVER:RIG_LeftArm
DRIVER:RIG_LeftForeArm
DRIVER:RIG_RightArm
DRIVER:RIG_RightForeArm
```

In Blender:
1. Import the FBX
2. Select the armature, go to Edit Mode
3. Rename each bone to match the list above
4. Export as FBX (Apply Modifiers: yes)

### 3. Convert to KN5

1. Open KS Editor
2. Import your prepared FBX
3. Assign materials and textures
4. Export as KN5
5. Name it `lm_yourcharacter.kn5`

### 4. Install

Copy the `.kn5` to:
```
apps/lua/Realistic Walking Camera/models/avatars/
```

### 5. Register

This step requires editing the main Lua file. Open `realistic walking camera.lua` and find `AvatarModels` (around line 879). Add your character. See the CUSTOM-CONTENT-GUIDE.md in the mod folder for the exact format.

## Adding Animations

### 1. Get an animation

On Mixamo, select your character, browse animations, download as FBX (60fps, With Skin, no Keyframe Reduction).

### 2. Convert to KSANIM

1. Import the animation FBX in Blender
2. Make sure bone names match `DRIVER:RIG_*`
3. Export as FBX (Bake Animation: yes)
4. Open in KS Editor, export as KSANIM

### 3. Install

Copy the `.ksanim` to the right subfolder:
- Walking: `models/walk/`
- Running: `models/run/`
- Idle: `models/idle/`
- Emotes: `models/emotes/`

### 4. Point your character config to the new animation files

In the `AvatarModels` table, set `animFile`, `runAnimFile`, etc. to your new ksanim files.

## Troubleshooting

**Model invisible** - Bones don't match. Double check every name is exactly `DRIVER:RIG_BoneName`.

**Model floating or underground** - Adjust `modelYOffset` in the config (try 0.0 to 1.0).

**Animation doesn't play** - The ksanim skeleton must match the model's skeleton exactly. Same bone names, same hierarchy.
