import bpy

from ...debug import DEBUG_EDIT_MATERIAL
from ...utils import get_pref


def set_shader_ball_mat(mat, coll):
    """导入并设置材质球模型/材质

    :param mat: bpy.types.Material
    :param coll: bpy.types.Collection
    :return:
    """
    # 获取设置
    with SaveUpdate():
        mat_pv_type = get_pref().shader_ball
        if mat_pv_type == 'NONE':
            mat_pv_type = mat.mathp_preview_render_type

        shader_ball_lib = Path(__file__).parent.parent.joinpath('shader_ball_lib')
        blend_file = shader_ball_lib.joinpath('shader_ball.blend')

        with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
            data_to.objects = [mat_pv_type]

        tmp_obj = data_to.objects[0]

        # 移动到比较远的地方
        tmp_obj.location = (10000, 10000, 10000)

        coll.objects.link(tmp_obj)

        # 设置激活项和材质
        bpy.context.view_layer.objects.active = tmp_obj

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.object.select_set(True)
        bpy.ops.object.shade_smooth()

        tmp_obj.select_set(True)
        tmp_obj.active_material = mat

        State.last_edit_mat = mat.name


class EditMaterial(bpy.types.Operator):
    bl_idname = 'mathp.edit_material_asset'
    bl_label = 'Edit Material Asset'

    new_window_hash = None
    edit_material = None
    count = None
    timer = None

    @classmethod
    def poll(cls, context):
        return (hasattr(context, 'selected_assets') and context.selected_assets) or context.asset

    def invoke(self, context, event):
        if res := self.execute(context):
            if "FINISHED" not in res:
                self.exit(context)
                return res
        if DEBUG_EDIT_MATERIAL:
            self.count = 0
            print("context.window", context.window, hash(context.window))
        self.timer = context.window_manager.event_timer_add(1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        for window in context.window_manager.windows:
            if hash(window) == self.new_window_hash:  # 找到弹出的窗口
                self.count += 1
                if DEBUG_EDIT_MATERIAL:
                    print(f"\rpass {self.count}", self.new_window_hash, end="", flush=True)
                return {"PASS_THROUGH"}

        self.exit(context)
        return {"FINISHED"}

    def execute(self, context):
        """执行弹出窗口"""
        if res := self.find_material(context):
            return res
        self.popup_window(context)
        return {'FINISHED'}

    def exit(self, context):
        if DEBUG_EDIT_MATERIAL:
            print("exit", self.new_window_hash, flush=True)
        context.window_manager.event_timer_remove(self.timer)
        self.new_window_hash = None
        self.edit_material = None

    def cancel(self, context):
        self.exit(context)
        print("cancel")
        print(self.edit_material)

    def popup_window(self, context):
        from ...utils import get_pref
        from ...utils.window import pop_up_window
        pref = get_pref()

        # 设置鼠标位置，以便弹窗出现在正中央
        w = context.window
        w_center_x, w_center_y = w.width / 2, w.height / 2
        w.cursor_warp(int(w_center_x), int(w_center_y))

        new_window = pop_up_window(pref.window_style)
        self.new_window_hash = hash(new_window)
        self.preview_3d(context, new_window)

    def find_material(self, context):
        from ...utils import get_local_selected_assets

        match_obj = get_local_selected_assets(context)
        selected_mat = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        if not selected_mat:
            self.report({'WARNING'}, '请选择一个本地材质资产')
            return {"CANCELLED"}

        self.edit_material = selected_mat[0]

    def preview_3d(self, context, window):
        from ...utils import get_pref, get_fbx_path
        pref = get_pref()

        print("preview_3d", hash(context.window))
        fbx_file = get_fbx_path(pref.shader_ball)
        bpy.ops.scene.new(type="EMPTY")
        bpy.ops.import_scene.fbx("EXEC_DEFAULT", filepath=fbx_file)
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
        return {'FINISHED'}
