Put the saved map files in this folder before running navigation:

- `map.yaml`
- the image file referenced by `map.yaml` (usually `map.pgm`)

Example:

```bash
rosrun map_server map_saver -f ~/robot/catkin_ws/src/robot_bringup/maps/map
```
