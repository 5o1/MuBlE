"""Render Xbox body-pose probes in the MuBlE table/light scene with Cycles."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import bpy
from mathutils import Matrix, Quaternion, Vector


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from muble.trace import validate_body_pose_trace


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-scene", type=Path, required=True)
    parser.add_argument("--visual-blend", type=Path, required=True)
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=64)
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pose_matrix(record):
    matrix = Quaternion(record["quaternion_wxyz"]).to_matrix().to_4x4()
    matrix.translation = Vector(record["position"])
    return matrix


def desk_top_and_center():
    desk = bpy.data.objects["Desk"]
    corners = [desk.matrix_world @ Vector(corner) for corner in desk.bound_box]
    return max(corner.z for corner in corners), Vector((desk.location.x, desk.location.y, 0))


def look_at(camera, position, target):
    camera.location = position
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = (target - position).to_track_quat("-Z", "Y")


def main():
    args = parse_args()
    base_scene = args.base_scene.resolve(strict=True)
    visual_blend = args.visual_blend.resolve(strict=True)
    binding_path = args.binding.resolve(strict=True)
    trace_path = args.trace.resolve(strict=True)
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    trace = validate_body_pose_trace(json.loads(trace_path.read_text(encoding="utf-8")))

    bpy.ops.wm.open_mainfile(filepath=str(base_scene))
    scene = bpy.context.scene
    for collection_name in ("Robot", "Gripper", "Objects"):
        collection = bpy.data.collections.get(collection_name)
        if collection:
            for obj in collection.all_objects:
                obj.hide_render = True

    object_names = [record["blender_object"] for record in binding["parts"].values()]
    with bpy.data.libraries.load(str(visual_blend), link=False) as (source, target):
        missing = sorted(set(object_names) - set(source.objects))
        if missing:
            raise RuntimeError(f"Xbox blend is missing objects: {missing}")
        target.objects = object_names
    collection = bpy.data.collections.new("Xbox One S")
    scene.collection.children.link(collection)
    loaded = {}
    for obj in target.objects:
        if obj is None:
            continue
        collection.objects.link(obj)
        loaded[obj.name] = obj
    bpy.context.view_layer.update()

    source_matrices = {}
    for name, obj in loaded.items():
        matrix = obj.matrix_world.copy()
        obj.parent = None
        obj.matrix_world = matrix
        source_matrices[name] = matrix

    top, center = desk_top_and_center()
    controller_half_height = 0.029858975586743625
    root_position = Vector((center.x, center.y, top + controller_half_height))
    table_transform = Matrix.Translation(root_position)
    source_to_sim = Matrix.Rotation(math.pi / 2, 4, "X")
    source_scale = Matrix.Scale(float(binding["meters_per_native_unit"]), 4)
    visual_root = table_transform @ source_to_sim @ source_scale

    neutral = trace["frames"][0]["bodies"]
    offsets = {}
    for part, record in binding["parts"].items():
        body = record["body"]
        obj = loaded[record["blender_object"]]
        body_neutral = table_transform @ pose_matrix(neutral[body])
        visual_neutral = visual_root @ source_matrices[obj.name]
        offsets[part] = body_neutral.inverted() @ visual_neutral

    camera_data = bpy.data.cameras.new("xbox_front_camera")
    camera = bpy.data.objects.new("xbox_front_camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera_data.sensor_fit = "VERTICAL"
    camera_data.angle = math.radians(35)
    camera_data.clip_start = 0.001
    camera_data.clip_end = 10
    camera_position = root_position + Vector((0.0, -0.32, 0.24))
    camera_target = root_position + Vector((0.0, 0.0, 0.0))
    look_at(camera, camera_position, camera_target)

    scene.render.engine = "CYCLES"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.cycles.samples = args.samples
    scene.cycles.transparent_min_bounces = 8
    scene.cycles.transparent_max_bounces = 8
    preferences = bpy.context.preferences.addons["cycles"].preferences
    preferences.compute_device_type = "OPTIX"
    preferences.get_devices()
    for device in preferences.devices:
        device.use = device.type == "OPTIX"
    scene.cycles.device = "GPU"

    args.output.mkdir(parents=True, exist_ok=True)
    rendered = []
    for frame, control in zip(trace["frames"], trace["controls"], strict=True):
        for part, record in binding["parts"].items():
            body_matrix = table_transform @ pose_matrix(frame["bodies"][record["body"]])
            loaded[record["blender_object"]].matrix_world = body_matrix @ offsets[part]
        bpy.context.view_layer.update()
        filename = f"frame_{frame['frame_index']:02d}_{control['label']}.png"
        scene.render.filepath = str(args.output / filename)
        started = time.perf_counter()
        bpy.ops.render.render(write_still=True)
        rendered.append({"file": filename, "seconds": time.perf_counter() - started})

    report = {
        "schema_version": 1,
        "status": "pending_user_visual_review",
        "blender": bpy.app.version_string,
        "base_scene": str(base_scene),
        "base_scene_sha256": sha256(base_scene),
        "visual_blend": str(visual_blend),
        "visual_blend_sha256": sha256(visual_blend),
        "trace": str(trace_path),
        "binding": str(binding_path),
        "parts": len(binding["parts"]),
        "camera": {
            "position": list(camera_position),
            "target": list(camera_target),
            "vertical_fov_degrees": 35,
        },
        "desk_top_z": top,
        "controller_root": list(root_position),
        "engine": "CYCLES",
        "samples": args.samples,
        "rendered": rendered,
    }
    (args.output / "result.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report))


if __name__ == "__main__":
    main()
