# Modernization evidence

These files record the first migration boundary for Python 3.12, MuJoCo 3.15,
robosuite 1.5.2 and Blender 4.5.9.

- `modern_environment.json`: imported runtime versions and base scene path;
- `tabletop_smoke.json`: empty MuBlE tabletop reset plus 100 composite-controller steps;
- `modern_eevee.{json,png}`: original MuBlE LFS scene loaded and rendered by Blender 4.5 EEVEE;
- `modern_cycles.{json,png}`: the same scene rendered by Blender 4.5 Cycles/OptiX on GPU3.

The records establish executable compatibility. They do not constitute visual
acceptance of a new task asset.
