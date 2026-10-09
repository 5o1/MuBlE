# Xbox gamepad probe

Status: pending user visual review.

The three `front` images use:

- MuBlE base scene SHA-256
  `349802ba355cedf1a657a92d82c06d91c4d489a9b2c15e551fc7bb54485951c8`;
- approved Xbox visual blend SHA-256
  `44fe631eb0ee395a70891ba6228bd9a6d4105343d97d263dfc416f2acf4ad8b0`;
- Blender 4.5.9 Cycles/OptiX, 64 samples, GPU3;
- one fixed 35-degree vertical-FOV front-high camera;
- body poses from the full-controls MuJoCo MJCF.

Files:

- `front/frame_00_neutral.png`;
- `front/frame_01_a_pressed.png`;
- `front/frame_02_left_stick_x_positive.png`;
- `probe_trace.json`: three frames of sixteen named body poses;
- `front/result.json`: source hashes, camera and render timings.
