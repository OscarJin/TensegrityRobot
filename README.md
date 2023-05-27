# Tensegrity Robot
Design, fabrication, control and simulation of tensegrity robots

## Dependencies
- Ubuntu
- Python 3.8.16 (Anaconda)
- Gymnasium 0.28.1 + Mujoco 2.3.3 (See [Documentation][gym-doc])
- Stable baselines 3 for Gymnasium (See [Installation][sb3-doc])
- Pytorch 1.13.1

[gym-doc]: https://gymnasium.farama.org/environments/mujoco/
[sb3-doc]: https://stable-baselines3.readthedocs.io/en/master/guide/install.html

## XML Builder for Tensegrity
The class `Tensegrity` in `src/TesengrityModel/tensegrity_builder.py` can automatically generate an XML model, which can be directly loaded by Mujoco.

Just input coordinates of nodes, pairs of bars and cables, and generate the XML model!
(Of course, `numpy.ndarray` is strongly recommended)

<u><i>Warning:</i></u>

The Mujoco model for tensegrity may not be accurate, since it has not yet been verified by the real world.

## Gymnasium Environment for Tensegrity
A Gymnasium environment has been built for tensegrity robots.

### Action Space

### Observation Space
Observations consist of position values of different parts of the tensegrity, followed by the velocities of these
parts.

By default, observations do not include the x- and y-coordinates of `bar1` of the tensegrity. These may be included
by passing `exclude_current_positions_from_obs=False` during construction.
In that case, the observation space will have 13*{number of bars} dimensions where the first two dimensions
represent the x- and y- coordinates of `bar1`.
Regardless of whether `exclude_current_positions_from_obs` was set to true or false, the x- and y-coordinates of
`bar1` will be returned in `info` with keys `"x_position"` and `"y_position"`, respectively.

However, by default, an observation is a `ndarray` with shape `(13*{number of bars}-2,)`

The (x,y,z) coordinates are translational DOFs while the orientations are rotational
DOFs expressed as quaternions.One can read more about free joints on the
[Mujoco Documentation][mujoco-doc].

[mujoco-doc]: https://mujoco.readthedocs.io/en/latest/XMLreference.html

### Rewards
The reward consists of three parts:
- *healthy_reward*: Every timestep that the tensegrity is healthy (see definition in section "Episode Termination"),
     it gets a reward of fixed value `healthy_reward`
- *forward_reward*: A reward of moving forward which is measured as
*(x-coordinate before action - x-coordinate after action)/dt*. *dt* is the time
between actions and is dependent on the `frame_skip` parameter (default is 5),
where the frametime is 0.01 - making the default *dt = 5 * 0.01 = 0.05*.
This reward would be positive if the tensegrity moves forward (in positive x direction).
- *ctrl_cost*: A negative reward for penalising the tensegrity if it takes actions
that are too large. It is measured as *`ctrl_cost_weight` * sum(action<sup>2</sup>)*
where *`ctr_cost_weight`* is a parameter set for the control and has a default value of 0.05.

The total reward returned is ***reward*** *=* *healthy_reward + forward_reward - ctrl_cost*.

### Starting State
All observations start in state with a uniform noise in the range
    of [-`reset_noise_scale`, `reset_noise_scale`] added to the positional values and standard normal noise
    with mean 0 and standard deviation `reset_noise_scale` added to the velocity values for
    stochasticity. The initial orientation is designed to make it face forward as well.

### Episode End
The tensegrity is said to be unhealthy if any of the following happens:

1. Any of the state space values is no longer finite
2. The z-coordinate of the tensegrity is **not** in the closed interval given by `healthy_z_range`
(defaults to [-0.2, 5.0])

If `terminate_when_unhealthy=True` is passed during construction (which is the default),
   the episode ends when any of the following happens:

1. Truncation: The episode duration reaches a 1000 timesteps
2. Termination: The tensengrity is unhealthy

If `terminate_when_unhealthy=False` is passed, the episode is ended only when 1000 timesteps are exceeded.

## Exploration of Tensegrity Design Space
GA is applied to explore the design space of tensegrity. To use GA, import `tensegrity_ga` and initiate the 
`TensegrityGA` class.
```python
import src.TensegrityModel.tensegrity_ga as ga
tensegrity_ga = ga.TensegrityGA(6)
tensegrity_ga.run()
print(tensegrity_ga.best_individual[0])
```

### Encoding
Please refer to the following article:

Paul, Chandana, Hod Lipson, and Francisco J. Valero Cuevas. "Evolutionary form-finding of tensegrity structures." 
_Proceedings of the 7th annual conference on Genetic and evolutionary computation._ 2005.

### Fitness

_Warning:_ Fitness function is still under development.

Temporarily, volume of the bounding box is selected as the fitness criterion.
