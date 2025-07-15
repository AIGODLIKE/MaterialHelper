from typing import Union

import bpy


class State:
    window_count: int = 1
    new_window: Union[bpy.types.Window, None] = None
    last_edit_mat: Union[bpy.types.Material, None] = None


def split_shader_3d_area():
    """用于切分设置实时预览area

    :return:
    """
    from . import get_pref
    screen = bpy.context.window_manager.windows[-1].screen
    screen.name = 'tmp_mathp'

    screen = bpy.context.window_manager.windows[-1].screen
    screen.name = 'tmp_mathp'

    area_shader = bpy.context.window_manager.windows[-1].screen.areas[0]
    # 拆分 拆分区域大的是原面板
    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.25)
    area_3d = bpy.context.window_manager.windows[-1].screen.areas[-1]
    # 更改窗口类型
    area_shader.type = 'NODE_EDITOR'
    area_shader.ui_type = 'ShaderNodeTree'

    # 窗口设置
    area_3d.type = 'VIEW_3D'
    space = area_3d.spaces[0]
    space.overlay.show_overlays = False
    space.show_gizmo = False
    space.region_3d.view_perspective = 'PERSP'

    shading_type = get_pref().shading_type

    space.shading.type = shading_type
    space.lock_object = bpy.context.object  # 锁定物体
    space.shading.use_scene_world_render = False
    space.shading.use_scene_lights_render = False
    space.shading.studio_light = 'city.exr'

    # set view
    space.region_3d.view_rotation = (0.62, 0.38, 0.35, 0.58)
    space.region_3d.view_location = (0.16, 0, 0.16)

    # solo
    override = {'area': area_3d}
    try:
        with bpy.context.temp_override(**override):
            bpy.ops.view3d.localview('INVOKE_DEFAULT')
    except RuntimeError:
        if 'tmp_mathp' in bpy.data.screens:
            # 清理多余screen
            for s in bpy.data.screens:
                if not s.name.startswith('tmp_mathp'): continue
                # 清除屏幕
                s.user_clear()
                # 清除局部视图
                for area in s.areas:
                    if area.type != 'VIEW_3D': continue
                    for region in area.regions:
                        if region.type != 'WINDOW': continue

                        override2 = {'area': area, 'region': region}  # override context
                        try:
                            with bpy.context.temp_override(**override2):
                                bpy.ops.view3d.view_selected(use_all_regions=False)
                        except:
                            pass
                        break

    # header
    space.show_region_header = False
    space.shading.studio_light = 'forest.exr'

    return area_shader, area_3d


def update_window_count():
    State.window_count = len(bpy.context.window_manager.windows)
    State.new_window = bpy.context.window_manager.windows[-1]


def window_style_big():
    """大窗口,左属性面板右节点面板

    :return:
    """
    update_window_count()
    bpy.ops.wm.window_new_main()  # 使用新窗口
    update_window_count()
    split_shader_3d_area()

def window_style_small(flip_header=True):
    """小面板

    :return:
    # 创建新窗口
    # bpy.ops.render.view_show('INVOKE_AREA')
    """
    from . import get_pref
    update_window_count()
    bpy.ops.screen.userpref_show("INVOKE_AREA")  # 使用偏好设置而不是渲染（版本更改导致渲染不再置顶）
    update_window_count()

    if get_pref().use_shader_ball_pv:
        area_3d, area_shader = split_shader_3d_area()
    else:
        screen = bpy.context.window_manager.windows[-1].screen
        screen.name = 'tmp_mathp'

        area_shader = screen.areas[0]
        area_shader.type = 'NODE_EDITOR'
        area_shader.ui_type = 'ShaderNodeTree'

    # 侧边栏
    bpy.context.space_data.show_region_ui = True if get_pref().show_UI else False
    # 翻转菜单栏
    for region in area_shader.regions:
        override = {'area': area_shader, 'region': region}
        if region == 'UI':
            if get_pref().UI_direction == 'LEFT':
                bpy.ops.screen.region_flip(override, 'INVOKE_DEFAULT')
        elif region == 'UI' and flip_header:
            bpy.ops.screen.region_flip(override, 'INVOKE_DEFAULT')

            # 3.2
            # with bpy.context.temp_override(**override):
            #     if flip_header: bpy.ops.screen.region_flip('INVOKE_DEFAULT')

        # 等待blender修复
        # if region.type == 'WINDOW':
        #     with bpy.context.temp_override(area=area, region=region):
        #         bpy.ops.node.view_all("INVOKE_AREA")


def pop_up_window(style='SMALL'):
    """

    :return:
    """
    if style == 'BIG':
        window_style_big()
    else:
        window_style_small()
    return bpy.context.window_manager.windows[-1]
