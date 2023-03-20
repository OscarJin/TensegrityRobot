# create scene.xml
import os.path as osp


def create_scene(path, floor_pos=-1):
    """
    Create scene.xml
    Args:
        path: absolute path of folder for storing scene.xml
        floor_pos: z position of floor, default -1

    Returns:

    """
    xml_path = 'scene.xml'
    xml_path = osp.join(path, xml_path)
    scene_file = open(xml_path, 'w')

    default_msg = """
<mujoco>

    <statistic extent="2" meansize=".05"/>

    <visual>
        <rgba haze="0.15 0.25 0.35 1"/>
        <quality shadowsize="2048"/>
        <map stiffness="700" shadowscale="0.5" fogstart="10" fogend="15" zfar="40" haze="0.3"/>
    </visual>

    <asset>
        <texture type="skybox" builtin="gradient" rgb1=".4 .6 .8" rgb2="0 0 0" width="800" height="800" mark="random" markrgb="1 1 1"/>
        <texture name="texplane" type="2d" builtin="checker" rgb1=".2 .3 .4" rgb2=".1 0.15 0.2"
            width="512" height="512" mark="cross" markrgb=".8 .8 .8"/>

        <material name="matplane" reflectance="0.3" texture="texplane" texrepeat="1 1" texuniform="true"/>
    </asset>
    """
    scene_file.write(default_msg)

    # world body
    world_body = f"""
    <worldbody>
        <light directional="true" diffuse=".8 .8 .8" specular=".2 .2 .2" pos="0 0 5" dir="0 0 -1"/>
        <geom name="floor"  pos="0 0 {floor_pos}" size="10 10 0.125" type="plane" material="matplane" condim="3" friction=".9 .05 .05"/>
    </worldbody>

    """
    scene_file.write(world_body)

    # visual
    visual = """
    <visual>
        <headlight ambient=".4 .4 .4" diffuse=".8 .8 .8" specular="0.1 0.1 0.1"/>
        <map znear=".01"/>
        <quality shadowsize="2048"/>
    </visual>
</mujoco>
    """
    scene_file.write(visual)

    scene_file.close()
