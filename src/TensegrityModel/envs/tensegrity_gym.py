import numpy as np
from gymnasium import utils
from gymnasium.envs.mujoco import MujocoEnv
from gymnasium.spaces import Box


DEFAULT_CAMERA_CONFIG = {
    "distance": 4.0,
}


class TensegEnv(MujocoEnv, utils.EzPickle):
    """
    ## Description

    The model is for tensegrity robots.

    ## Action Space

    ## Observation Space

    Observations consist of position values of different parts of the tensegrity, followed by the velocities of these
    parts.

    By default, observations do not include the x- and y-coordinates of `bar1` of the tensegrity. These may be included
    by passing `exclude_current_positions_from_obs=False` during construction.
    In that case, the observation space will have 13*{number of bars} dimensions where the first two dimensions
    represent the x- and y- coordinates of the ant's torso.
    Regardless of whether `exclude_current_positions_from_obs` was set to true or false, the x- and y-coordinates of
    `bar1` will be returned in `info` with keys `"x_position"` and `"y_position"`, respectively.

    However, by default, an observation is a `ndarray` with shape `(13*{number of bars}-2,)`

    The (x,y,z) coordinates are translational DOFs while the orientations are rotational
    DOFs expressed as quaternions.One can read more about free joints on the
    [Mujoco Documentation](https://mujoco.readthedocs.io/en/latest/XMLreference.html).

    ## Rewards
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

    ## Starting State
    All observations start in state with a uniform noise in the range
    of [-`reset_noise_scale`, `reset_noise_scale`] added to the positional values and standard normal noise
    with mean 0 and standard deviation `reset_noise_scale` added to the velocity values for
    stochasticity. The initial orientation is designed to make it face forward as well.

    ## Episode End
    The tensegrity is said to be unhealthy if any of the following happens:

    1. Any of the state space values is no longer finite
    2. The z-coordinate of the tensegrity is **not** in the closed interval given by `healthy_z_range`
    (defaults to [-0.2, 5.0])

    If `terminate_when_unhealthy=True` is passed during construction (which is the default),
    the episode ends when any of the following happens:

    1. Truncation: The episode duration reaches a 1000 timesteps
    2. Termination: The ant is unhealthy

    If `terminate_when_unhealthy=False` is passed, the episode is ended only when 1000 timesteps are exceeded.

    """

    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array"
        ],
        "render_fps": 100
    }

    def __init__(
            self,
            xml_file,
            bar_num,
            ctrl_cost_weight=0.05,
            healthy_reward=1.0,
            terminate_when_unhealthy=True,
            healthy_z_range=(-.2, 5.0),
            reset_noise_scale=0.05,
            exclude_current_positions_from_obs=True,
            **kwargs,
    ):
        utils.EzPickle.__init__(
            self,
            xml_file,
            bar_num,
            ctrl_cost_weight,
            healthy_reward,
            terminate_when_unhealthy,
            healthy_z_range,
            reset_noise_scale,
            exclude_current_positions_from_obs,
            **kwargs,
        )

        self._bar_num = bar_num

        self._ctrl_cost_weight = ctrl_cost_weight

        self._healthy_reward = healthy_reward
        self._terminate_when_unhealthy = terminate_when_unhealthy
        self._healthy_z_range = healthy_z_range

        self._reset_noise_scale = reset_noise_scale

        self._exclude_current_positions_from_obs = (
            exclude_current_positions_from_obs
        )

        # Observation Space
        obs_shape = (7 + 6) * self._bar_num
        if exclude_current_positions_from_obs:
            obs_shape -= 2

        observation_space = Box(low=-np.inf, high=np.inf, shape=(obs_shape,), dtype=np.float64)

        # Mujoco Env
        MujocoEnv.__init__(
            self,
            xml_file,
            5,
            observation_space=observation_space,
            default_camera_config=DEFAULT_CAMERA_CONFIG,
            **kwargs,
        )

    @property
    def is_healthy(self):
        state = self.state_vector()
        min_z, max_z = self._healthy_z_range
        is_healthy = np.isfinite(state).all() and min_z <= state[2] <= max_z
        return is_healthy

    @property
    def healthy_reward(self):
        return (self.is_healthy or self._terminate_when_unhealthy) * self._healthy_reward

    def ctrl_cost(self, action):
        ctrl_cost = self._ctrl_cost_weight * np.sum(np.square(action))
        return ctrl_cost

    @property
    def terminated(self):
        terminated = not self.is_healthy if self._terminate_when_unhealthy else False
        return terminated

    def _get_obs(self):
        position = self.data.qpos.flat.copy()
        velocity = self.data.qvel.flat.copy()

        if self._exclude_current_positions_from_obs:
            position = position[2:]

        return np.concatenate((position, velocity))

    def step(self, action):
        xy_position_before = self.get_body_com("bar1")[:2].copy()
        self.do_simulation(action, self.frame_skip)
        xy_position_after = self.get_body_com("bar1")[:2].copy()

        xy_velocity = (xy_position_after - xy_position_before) / self.dt
        x_velocity, y_velocity = xy_velocity

        forward_reward = x_velocity
        healthy_reward = self.healthy_reward

        rewards = forward_reward + healthy_reward

        costs = ctrl_cost = self.ctrl_cost(action)

        reward = rewards - costs

        terminated = self.terminated

        observation = self._get_obs()

        info = {
            "reward_forward": forward_reward,
            "reward_ctrl": -ctrl_cost,
            "reward_health": healthy_reward,
            "x_position": xy_position_after[0],
            "y_position": xy_position_after[1],
            "distance_from_origin": np.linalg.norm(xy_position_after, ord=2),
            "x_velocity": x_velocity,
            "y_velocity": y_velocity,
        }

        if self.render_mode == "human":
            self.render()

        return observation, reward, terminated, False, info

    def reset_model(self):
        noise_low = -self._reset_noise_scale
        noise_high = self._reset_noise_scale

        qpos = self.init_qpos + self.np_random.uniform(low=noise_low, high=noise_high, size=self.model.nq)
        qvel = (self.init_qvel + self._reset_noise_scale * self.np_random.standard_normal(self.model.nv))
        self.set_state(qpos, qvel)

        observation = self._get_obs()

        return observation
