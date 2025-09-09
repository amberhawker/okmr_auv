# okmr_controls

The okmr_controls package contains code for low level AUV control systems.

## Purpose
The code in this package is an updated / revised version of okmr_controls_old.
It serves the same general purpose (i.e. PID control and thrust allocation) with several improvements:

- written in c++ to significantly reduce cpu usage compared to python
- seperates the control system into 5 layers (pose -> velocity -> acceleration -> thrust -> throttle)
- implements a robust and flexible thrust allocator that can support any thruster configuration
- implements control layers (ex. pose, velocity) as one node, as opposed to six nodes (one per axis)
- allows dynamic reconfiguration of pid controller gains, allowing live tuning

## Nodes

### pid_controller
Not an actual node, but rather a non-ros2 class that can be used to do 
[PID controller](https://en.wikipedia.org/wiki/Proportional%E2%80%93integral%E2%80%93derivative_controller)
calculations. Used by the control_layer_base.

### control_layer_base
Abstract class that defines common behaviour for all control layers
This includes:
- gain parameter handling
- 6 pid controllers (one for each axis)
- rate based updating (using ros2 timers)

All PID calculations are done in one function call to compute_layer_command().
This is generally done inside the update() method, which is to be implemented by implementations of tbe base class (ex. pose_control_layer)

### pose_control_layer
TODO

### velocity_control_layer
TODO

### accel_control_layer
TODO

### thrust_allocator
TODO

## Future Work

- Improved thruster allocation. Minimize power consumption using some kind of optimization based approach.
- Introduce auto-tuning or some kind of real time adaptation

