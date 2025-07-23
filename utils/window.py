import bpy

PREVIEW_KEY = "Material Helper Preview"


def saved_one_area(context, window):
    """只保留一个区域"""
    screen = context.window.screen
    while len(screen.areas) != 1:
        with context.temp_override(window=window, screen=screen, area=screen.areas[-1]):
            bpy.ops.screen.area_close()


def split_3d_area(window):
    from . import get_pref
    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.25)
    screen = window.screen
    area_3d = screen.areas[-1]

    # 窗口设置
    area_3d.type = 'VIEW_3D'
    space = [s for s in area_3d.spaces if s.type == "VIEW_3D"][0]
    space.overlay.show_overlays = False
    space.show_gizmo = False
    space.region_3d.view_perspective = 'PERSP'

    space.shading.type = get_pref().shading_type
    space.shading.use_scene_world_render = False
    space.shading.use_scene_lights_render = False
    space.shading.studio_light = 'city.exr'

    # set view
    space.region_3d.view_rotation = (0.62, 0.38, 0.35, 0.58)
    space.region_3d.view_location = (0.16, 0, 0.16)

    # header
    space.show_region_header = False
    space.shading.studio_light = 'forest.exr'
    return area_3d


def switch_to_node_tree_area(window):
    """切换到节点界面"""
    node_area = window.screen.areas[0]
    node_area.type = 'NODE_EDITOR'
    node_area.ui_type = 'ShaderNodeTree'
    return node_area


class PreviewMaterialWindow:
    window = None
    area_node = None
    area_3d = None
    waiting_for_deletion_objects = []
    waiting_for_deletion_mesh_data = []
    window_fullscreen = []

    def __init__(self, ops, context, event, material):
        # 设置鼠标位置，以便弹窗出现在正中央
        # mouse_x, mouse_y = event.mouse_x, event.mouse_y
        win = context.window
        win.cursor_warp(int(win.width / 2), int(win.height / 2))

        self.material = material
        self.ops = ops
        self.new_window(context)

        # win.cursor_warp(mouse_x, mouse_y)

    @classmethod
    def check_full_window(cls, window):
        return hash(window) in cls.window_fullscreen

    def new_window(self, context) -> bpy.types.Window:
        from . import get_pref
        pref = get_pref()

        # add a window
        style = pref.window_style
        if style == "SMALL":  # 小窗口用偏好设置
            bpy.ops.screen.userpref_show()
        else:
            bpy.ops.wm.window_new()
        self.window = window = context.window_manager.windows[-1]  # 创建的新窗口
        if style == "FULL_SCREEN":
            with context.temp_override(window=window):
                bpy.ops.wm.window_fullscreen_toggle()
            PreviewMaterialWindow.window_fullscreen.append(hash(window))
        self.window.screen.name = PREVIEW_KEY
        # handle a window type and count
        saved_one_area(context, window)
        self.area_node = switch_to_node_tree_area(window)
        if get_pref().use_shader_ball_preview:
            self.area_3d = split_3d_area(window)

        self.create_preview_object(context)

    def create_preview_object(self, context):
        """创建预览的物体,如果需要添加就加在需要删除的里面"""
        from . import get_pref
        from ..src.preview_object import from_blend_import_object
        pref = get_pref()
        preview_render_type = pref.preview_render_type

        selected_objects = context.selected_objects
        mat = self.material
        if len(selected_objects) == 1 and selected_objects[-1].type == "MESH":  # 只选择一个物体
            active_object = selected_objects[-1]
            new_obj = active_object.copy()
            new_obj.data.materials.clear()
            new_obj.name = f"{PREVIEW_KEY} {active_object.name}"
            active_object = new_obj
            context.scene.collection.objects.link(active_object)
            self.waiting_for_deletion_objects.append(active_object.name)
        else:
            # 没选择物体或选择了多个物体,导入预览物体
            if preview_render_type == 'NONE':
                preview_render_type = mat.preview_render_type
            active_object = from_blend_import_object(preview_render_type)
            mesh = active_object.data
            self.waiting_for_deletion_mesh_data.append(mesh.name)
            name = f"{PREVIEW_KEY} {preview_render_type}"
            mesh.name = name
            active_object.name = name
            context.scene.collection.objects.link(active_object)
            context.view_layer.objects.active = active_object
            active_object.select_set(True)
            with context.temp_override(object=active_object, active_object=active_object,
                                       selected_objects=[active_object, ]):
                bpy.ops.object.shade_smooth()

        active_object.active_material = mat
        context.view_layer.objects.active = active_object
        loc = 1000
        active_object.location = (loc, loc, loc)
        active_object.select_set(True)
        bpy.ops.object.select_all(action='DESELECT')

        self.preview_lock(context, active_object)

    def preview_lock(self, context, obj):
        """
        set(i.type for i in bpy.context.area.spaces)
        {'GRAPH_EDITOR', 'VIEW_3D', 'NODE_EDITOR', 'DOPESHEET_EDITOR', 'INFO', 'FILE_BROWSER', 'OUTLINER',
         'SEQUENCE_EDITOR', 'TEXT_EDITOR', 'PROPERTIES', 'CLIP_EDITOR', 'NLA_EDITOR', 'CONSOLE'}"""
        area = self.area_3d
        if area:
            space = [s for s in area.spaces if s.type == "VIEW_3D"][0]
            region = [r for r in area.regions if r.type == "WINDOW"][0]
            context.view_layer.objects.active = obj
            obj.select_set(True)
            space.lock_object = obj  # 锁定物体
            with context.temp_override(
                    object=obj,
                    active_object=obj,
                    selected_objects=[obj, ],
                    area=area,
                    region=region,
            ):
                bpy.ops.view3d.view_selected("EXEC_DEFAULT")
                bpy.ops.view3d.localview("EXEC_DEFAULT")

    def exit(self):
        for obj_name in self.waiting_for_deletion_objects:
            if obj := bpy.data.objects.get(obj_name):
                bpy.data.objects.remove(obj)
        for mesh_name in self.waiting_for_deletion_mesh_data:
            if mesh := bpy.data.meshes.get(mesh_name):
                bpy.data.meshes.remove(mesh)
        wh = hash(self.window)
        if wh in PreviewMaterialWindow.window_fullscreen:
            PreviewMaterialWindow.window_fullscreen.remove(wh)

    def check(self, ops, context):
        for window in context.window_manager.windows:
            if hash(window) == hash(self.window):  # 找到弹出的窗口
                ops.count += 1
                return True
        return False

    def try_show_all_node(self, ops, context):
        if hasattr(ops, "is_show_all_node"):
            return
        from . import get_pref
        pref = get_pref()
        node_area = self.area_node
        flip_header = False
        # 侧边栏
        context.space_data.show_region_ui = pref.show_ui_panel
        space = [s for s in node_area.spaces if s.type == "NODE_EDITOR"][0]
        for region in node_area.regions:
            override = {'area': node_area, 'region': region, "space_data": space}
            with context.temp_override(**override):
                if region.type == 'WINDOW':  # 显示所有节点
                    bpy.ops.node.view_all("EXEC_DEFAULT")
                if region.type == 'UI':  # 翻转菜单栏
                    if pref.ui_direction == 'LEFT':
                        bpy.ops.screen.region_flip()
                    elif flip_header:
                        bpy.ops.screen.region_flip()

        setattr(ops, "is_show_all_node", True)

    @staticmethod
    def clear_temp_preview_data():
        clear_list = []
        for obj in bpy.data.objects:
            if PREVIEW_KEY in obj.name:
                clear_list.append(obj.name)
                bpy.data.objects.remove(obj)
        for mesh in bpy.data.meshes:
            if PREVIEW_KEY in mesh.name:
                clear_list.append(mesh.name)
                bpy.data.meshes.remove(mesh)
        cl = len(clear_list)
        if cl != 0:
            print(f"Material Helper Clear temp preview {cl} data: {clear_list}")
