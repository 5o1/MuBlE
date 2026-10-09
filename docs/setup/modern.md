---
layout: default
title: Modern runtime
parent: Setup
nav_order: 3
---

# Modern runtime

The maintained runtime target is:

- Python 3.12;
- MuJoCo 3.15;
- robosuite 1.5.2;
- NumPy 1.26.4 (required by Mink 0.0.5);
- OpenCV 4.10.0;
- Blender 4.5 LTS as an external executable.

The original Python 3.7 / Blender 2.83 / `mujoco_py` installation remains in
the repository for historical reproducibility. It is not the modern runtime.
Do not replace Blender's bundled Python and do not edit robosuite files inside
`site-packages`.

Create a dedicated Python 3.12 environment and install:

```bash
python -m pip install -e '.[test]'
```

robosuite 1.5.2 requires two source-level compatibility changes for MuJoCo
3.15: integer joint-type comparisons and the new `mj_fullM(model, data, dst)`
signature. Clone the exact upstream commit and apply the checked-in patch:

```bash
git clone --branch v1.5.2 --depth 1 \
  https://github.com/ARISE-Initiative/robosuite.git /path/to/robosuite-1.5.2
python scripts/prepare_robosuite_source.py /path/to/robosuite-1.5.2
python -m pip install --no-deps -e /path/to/robosuite-1.5.2
```

For custom MuJoCo wheels built with a newer `libstdc++`, copy the activation
and deactivation hooks from `requirements/{activate,deactivate}.d` into the
environment. Verify the complete runtime explicitly:

```bash
python scripts/verify_modern_environment.py \
  --blender /path/to/blender-4.5/blender \
  --base-scene scene_generation/data/base_scene_panda.blend
```

`muble.MujocoRuntime` is the official-MuJoCo entry point for new integrations.
The legacy `TabletopEnv` now targets robosuite 1.5's `ManipulationEnv` and uses
its composite controller path by default. MuBlE's old custom OSC is disabled
until its controller implementation is ported separately.

Run the migrated tabletop smoke test with:

```bash
python scripts/smoke_modern_tabletop.py \
  --steps 100 --output results/modernization/tabletop_smoke.json
```
