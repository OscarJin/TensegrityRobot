# Tensegrity Robot
Design, fabrication, control and simulation of tensegrity robots

## Dependencies
- Ubuntu
- Python 3.8.16 (Anaconda)
- Gymnasium 0.28.1 + Mujoco 2.3.3 (See [Documentation][gym-doc])
- Stable baselines 3 for Gymnasium (See [installation][sb3-doc])
- Pytorch 1.13.1

[gym-doc]: https://gymnasium.farama.org/environments/mujoco/
[sb3-doc]: https://stable-baselines3.readthedocs.io/en/master/guide/install.html

## XML Builder for Tensegrity
The class `Tensegrity` in `src/TesengrityModel/tensegrity_builder.py` can automatically generate an XML model, which can be directly loaded by Mujoco.

Just input coordinates of nodes, pairs of bars and cables, and generate the XML model!

<u><i>Warning:</i></u>

The Mujoco model for tensegrity may not be accurate, since it has not yet been verified by the real world.