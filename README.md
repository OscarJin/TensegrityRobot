# Tensegrity Robot
Design, fabrication, control and simulation of tensegrity robots

## Dependencies
- Ubuntu
- Mujoco 2.1.0, mujoco-py
- Python 3.8.15 (Anaconda)

(Reference: [Ubuntu20.04安装mujoco][csdn])

[csdn]: https://blog.csdn.net/qq_47997583/article/details/125400418

## XML Builder for Tensegrity
The class `Tensegrity` in `src/TesengrityModel/tensegrity_builder.py` can automatically generate an XML model, which can be directly loaded by Mujoco.

Just input coordinates of nodes, pairs of bars and cables, and generate the XML model!

<u><i>Warning:</i></u>

The Mujoco model for tensegrity may not be accurate, since it has not yet been verified by the real world.