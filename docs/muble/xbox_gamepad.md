---
layout: default
title: Xbox gamepad integration
parent: MuBlE
nav_order: 6
---

# Xbox gamepad integration

This integration keeps physics and appearance in separate source repositories:

- the Xbox `full_controls_estimated_v0` MJCF supplies twenty joints and named
  body poses;
- MuBlE supplies the table, Ground, Key/Fill/Back area lights and the original
  additional sun light;
- `Xbox_One_S_approved_cycles.blend` supplies sixteen visual meshes and its
  original material graph.

No MuJoCo texture or Filament material is used by the Blender output.

## Pose transport

`integrations/xbox_gamepad/export_pose_probe.py` loads the MJCF with the modern
official-MuJoCo runtime and writes a `muble/body-pose-trace-v1` trace. The trace
contains `xpos` and `xquat` for every body referenced by the sixteen-part
binding.

`muble_blender/render_xbox_pose_probe.py` opens Blender 4.5, loads the MuBlE
base scene, appends only the approved Xbox mesh objects, clears their artist
bone parenting, and computes a neutral body-to-visual offset for each part:

```text
offset = inverse(neutral_body_pose) × neutral_visual_pose
visual_pose(t) = body_pose(t) × offset
```

The scene uses one fixed front-high camera for every frame. The current probe
contains neutral, A-pressed and positive-left-stick-X states. Its status is
`pending_user_visual_review`; the three images are under
`results/xbox_gamepad_probe/front`.

## Commands

```bash
python integrations/xbox_gamepad/export_pose_probe.py \
  --xbox-package /path/to/xbox_gamepad_physics \
  --output /tmp/xbox_probe_trace.json

CUDA_VISIBLE_DEVICES=3 blender --background \
  --python muble_blender/render_xbox_pose_probe.py -- \
  --base-scene scene_generation/data/base_scene_panda.blend \
  --visual-blend /path/to/Xbox_One_S_approved_cycles.blend \
  --binding integrations/xbox_gamepad/blender_binding.json \
  --trace /tmp/xbox_probe_trace.json \
  --output /tmp/xbox_probe_render \
  --samples 64
```
