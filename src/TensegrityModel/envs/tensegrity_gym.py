import numpy as np
from gymnasium import utils
from gymnasium.envs.mujoco import MujocoEnv
from gymnasium.spaces import Box


DEFAULT_CAMERA_CONFIG = {
    "distance": 4.0,
}


class TensegEnv(MujocoEnv, utils.EzPickle):

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
