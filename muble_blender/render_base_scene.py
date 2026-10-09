"""Blender 4.5 entry point for the unmodified MuBlE base scene."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

import bpy


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-scene", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--camera", default="cam1")
    parser.add_argument("--engine", choices=("cycles", "eevee"), default="cycles")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--gpu", action="store_true")
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])


def main():
    args = parse_args()
    source = args.base_scene.resolve(strict=True)
    output = args.output.resolve()
    report_path = args.report.resolve()
    if args.width <= 0 or args.height <= 0 or args.samples <= 0:
        raise ValueError("width, height and samples must be positive")

    bpy.ops.wm.open_mainfile(filepath=str(source))
    scene = bpy.context.scene
    required = ("Desk", "Ground", "Lamp_Key", "Lamp_Fill", "Lamp_Back")
    missing = [name for name in required if name not in bpy.data.objects]
    if missing:
        raise RuntimeError(f"MuBlE base scene is missing objects: {missing}")
    if args.camera not in bpy.data.objects:
        raise RuntimeError(f"MuBlE base scene has no camera {args.camera!r}")
    camera = bpy.data.objects[args.camera]
    if camera.type != "CAMERA":
        raise RuntimeError(f"{args.camera!r} is not a Blender camera")

    scene.camera = camera
    scene.render.engine = "CYCLES" if args.engine == "cycles" else "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(output)
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1

    if args.engine == "cycles":
        scene.cycles.samples = args.samples
        scene.cycles.transparent_min_bounces = 8
        scene.cycles.transparent_max_bounces = 8
        if args.gpu:
            preferences = bpy.context.preferences.addons["cycles"].preferences
            preferences.compute_device_type = "OPTIX"
            preferences.get_devices()
            for device in preferences.devices:
                device.use = device.type == "OPTIX"
            scene.cycles.device = "GPU"
        else:
            scene.cycles.device = "CPU"
    elif hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = args.samples

    output.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    bpy.ops.render.render(write_still=True)
    elapsed = time.perf_counter() - started
    report = {
        "schema_version": 1,
        "blender": bpy.app.version_string,
        "source": str(source),
        "output": str(output),
        "engine": scene.render.engine,
        "camera": camera.name,
        "resolution": [args.width, args.height],
        "samples": args.samples,
        "gpu_requested": args.gpu,
        "render_seconds": elapsed,
        "required_scene_objects": list(required),
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
