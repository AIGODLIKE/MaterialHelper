import bpy


def close_to_one_area(context, window):
    """只保留一个区域"""
    screen = context.window.screen
    while len(screen.areas) != 1:
        with context.temp_override(window=window, screen=screen, area=screen.areas[-1]):
            bpy.ops.screen.area_close()


def split_3d_area(context, window, material):
    from . import get_pref
    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.25)
    screen = window.screen
    area_3d = screen.areas[-1]

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

    # # solo
    # override = {'area': area_3d, 'screen': screen}
    # try:
    #     with bpy.context.temp_override(**override):
    #         bpy.ops.view3d.localview('INVOKE_DEFAULT')
    # except RuntimeError:
    #     if 'tmp_mathp' in bpy.data.screens:
    #         # 清理多余screen
    #         for s in bpy.data.screens:
    #             if not s.name.startswith('tmp_mathp'): continue
    #             # 清除屏幕
    #             s.user_clear()
    #             # 清除局部视图
    #             for area in s.areas:
    #                 if area.type != 'VIEW_3D': continue
    #                 for region in area.regions:
    #                     if region.type != 'WINDOW': continue
    #
    #                     override2 = {'area': area, 'region': region}  # override context
    #                     try:
    #                         with bpy.context.temp_override(**override2):
    #                             bpy.ops.view3d.view_selected(use_all_regions=False)
    #                     except:
    #                         pass
    #                     break

    # header
    space.show_region_header = False
    space.shading.studio_light = 'forest.exr'


def create_preview_view_layer(context, window, preview_material):
    ...
    # bpy.ops.scene.view_layer_add()


def create_preview_object(context, window, preview_material):
    selected_objects = context.selected_objects
    print("selected_objects", selected_objects)
    if len(selected_objects) == 1 and selected_objects[-1].type == "MESH":  # 只选择一个物体
        active_object = selected_objects[-1]
        if preview_material in active_object.data.materials:  # 材质在物体材质槽内，独立化物体即可
            ...
        else:
            # 没在材质槽内,添加材质到物体内并独立
            ...
    else:
        # 没选择物体或选择了多个物体,导入预览物体
        ...


def create_node_area(context, window, flip_header=True):
    from . import get_pref
    pref = get_pref()

    node_area = window.screen.areas[0]
    node_area.type = 'NODE_EDITOR'
    node_area.ui_type = 'ShaderNodeTree'
    print("selected_objects", context.selected_objects)

    # 侧边栏
    context.space_data.show_region_ui = pref.show_ui_panel
    for region in node_area.regions:
        override = {'area': node_area, 'region': region}
        with context.temp_override(**override):

            if region.type == 'UI':  # 翻转菜单栏
                if pref.ui_direction == 'LEFT':
                    bpy.ops.screen.region_flip()
                elif flip_header:
                    bpy.ops.screen.region_flip()

            if region.type == 'WINDOW':
                bpy.ops.node.view_all("INVOKE_DEFAULT")


def split_area(context, window, preview_material):
    """拆分区域"""
    from . import get_pref

    close_to_one_area(context, window)
    create_node_area(context, window)

    if get_pref().use_shader_ball_preview:
        split_3d_area(context, window, preview_material)


def new_window(context, preview_material) -> bpy.types.Window:
    from . import get_pref
    style = get_pref().window_style

    if style == "SMALL":  # 小窗口用偏好设置
        bpy.ops.screen.userpref_show()
    else:
        bpy.ops.wm.window_new()

    window = context.window_manager.windows[-1]
    if style == "FULL_SCREEN":
        with context.temp_override(window=window):
            bpy.ops.wm.window_fullscreen_toggle()

    split_area(context, window, preview_material)


def pop_up_preview_material_window(context, preview_material):
    window = new_window(context, preview_material)

    return window


def preview_3d(self, context, window):
    from . import get_pref
    pref = get_pref()

    print("preview_3d", hash(context.window))
    return
    # 创建集合
    tmp_coll = bpy.data.collections[
        'tmp_mathp'] if 'tmp_mathp' in bpy.data.collections else bpy.data.collections.new(
        'tmp_mathp')
    if 'tmp_mathp' not in context.scene.collection.children:
        context.scene.collection.children.link(tmp_coll)

    # 设置材质球/材质

    set_shader_ball_mat(selected_mat[0], tmp_coll)
    selected_mat[0].asset_generate_preview()
