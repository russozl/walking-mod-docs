
import bpy
import json
import math

def export_camera_to_walking_mod(camera_name="WalkingCamera", output_path=None, export_type="dolly"):
    """
    Export a Blender camera animation for the Walking Mod.
    
    export_type:
        "dolly"  - Exports as dolly keyframes (position + direction + fov + roll)
        "motion" - Exports as camera motion JSON (relative offsets for head bob)
    """
    cam = bpy.data.objects.get(camera_name)
    if not cam:
        print(f"Camera '{camera_name}' not found!")
        return
    
    scene = bpy.context.scene
    fps = scene.render.fps
    
    if not output_path:
        output_path = bpy.path.abspath("//") + f"exported_{export_type}.json"
    
    if export_type == "dolly":
        # === DOLLY EXPORT ===
        # Position, direction, FOV, roll for each keyframe
        keyframes = []
        
        # Sample every N frames (or use actual keyframes)
        sample_interval = max(1, fps // 4)  # 4 samples per second
        
        for frame in range(scene.frame_start, scene.frame_end + 1, sample_interval):
            scene.frame_set(frame)
            
            loc = cam.matrix_world.translation
            # Camera looks down -Z in local space, convert to world direction
            direction = cam.matrix_world.to_3x3() @ mathutils.Vector((0, 0, -1))
            direction.normalize()
            
            # Get FOV from focal length
            fov = math.degrees(cam.data.angle)
            
            # Get roll from camera rotation
            roll = math.degrees(cam.rotation_euler.y) if cam.rotation_mode == 'XYZ' else 0
            
            keyframes.append({
                "px": round(loc.x, 4),
                "py": round(loc.z, 4),   # Blender Z = AC Y (up)
                "pz": round(-loc.y, 4),  # Blender -Y = AC Z (forward)
                "dx": round(direction.x, 4),
                "dy": round(direction.z, 4),
                "dz": round(-direction.y, 4),
                "fov": round(fov, 1),
                "roll": round(roll, 2),
                "easing": 2  # SMOOTH
            })
        
        data = {
            "name": camera_name,
            "playback": {
                "duration": (scene.frame_end - scene.frame_start) / fps,
                "mode": 1,           # ONCE
                "interpolation": 2,  # CATMULL_ROM
                "easing": 2          # SMOOTH
            },
            "tracking": {
                "enabled": False,
                "targetCar": None,
                "lookAhead": 0.1
            },
            "keyframes": keyframes
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Exported {len(keyframes)} dolly keyframes to {output_path}")
        print(f"Duration: {data['playback']['duration']:.1f}s at {fps}fps")
    
    elif export_type == "motion":
        # === MOTION EXPORT ===
        # Relative offsets from a base position (for head bob / handheld feel)
        frames_data = []
        
        # Get base position (first frame)
        scene.frame_set(scene.frame_start)
        base_loc = cam.location.copy()
        base_rot = cam.rotation_euler.copy()
        
        for frame in range(scene.frame_start, scene.frame_end + 1):
            scene.frame_set(frame)
            
            loc = cam.location
            rot = cam.rotation_euler
            
            frames_data.append({
                "ox": round(loc.x - base_loc.x, 6),
                "oy": round(loc.z - base_loc.z, 6),  # Vertical offset
                "oz": round(-(loc.y - base_loc.y), 6),  # Forward offset
                "pitch": round(math.degrees(rot.x - base_rot.x), 4),
                "yaw": round(math.degrees(rot.z - base_rot.z), 4),
                "roll": round(math.degrees(rot.y - base_rot.y), 4)
            })
        
        data = {
            "name": camera_name,
            "fps": fps,
            "loop": True,
            "type": "walk",
            "frames": frames_data
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Exported {len(frames_data)} motion frames to {output_path}")
        print(f"Duration: {len(frames_data)/fps:.2f}s at {fps}fps")

# Usage:
# export_camera_to_walking_mod("WalkingCamera", "C:/path/to/output.json", "dolly")
# export_camera_to_walking_mod("WalkingCamera", "C:/path/to/output.json", "motion")
