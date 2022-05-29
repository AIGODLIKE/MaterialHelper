import bpy
from bpy.types import Operator
from bpy.props import (IntProperty, FloatProperty, StringProperty, EnumProperty, BoolProperty)
from bpy.types import GizmoGroup


def get_local_selected_assets(context):
    """获取选择的本地资产
    :param context: bpy.context
    :return: 选择项里的本地资产(任何资产类型) bpy.types.Object/Material/World
    """
    cur_lib_name = context.area.spaces.active.params.asset_library_ref
    match_obj = [asset_file.local_id for asset_file in context.selected_asset_files if
                 cur_lib_name == "LOCAL"]

    return match_obj


def pop_up_window(area_type='NODE_EDITOR', ui_type=None, size_x=1200, size_y=800):
    """ 弹窗
    :param area_type: 区域类型 str
    :parm ui_type: 区域ui类型 str
    :return:
    """

    window = bpy.context.scene.render
    # 储存类型
    ori_res_x = window.resolution_x
    ori_res_y = window.resolution_y
    ori_res_scale = window.resolution_percentage
    # 设置窗口尺寸
    window.resolution_x = size_x
    window.resolution_y = size_y
    window.resolution_percentage = 100
    # 呼出窗口
    # bpy.ops.render.view_show('INVOKE_AREA')  # 创建新窗口
    bpy.ops.screen.userpref_show("INVOKE_AREA")  # 使用偏好设置而不是渲染（版本更改导致渲染不再置顶）
    # bpy.ops.screen.region_flip('INVOKE_AREA')
    area = bpy.context.window_manager.windows[-1].screen.areas[0]
    # 更改窗口类型
    area.type = area_type
    bpy.context.space_data.show_region_ui = False  # 侧边栏
    if ui_type is not None:
        area.ui_type = ui_type
    # 恢复
    window.resolution_x = ori_res_x
    window.resolution_y = ori_res_y
    window.resolution_percentage = ori_res_scale


class MATHP_OT_edit_material_asset(Operator):
    bl_idname = 'mathp.edit_material_asset'
    bl_label = 'Edit Material Asset'

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'selected_asset_files') and context.selected_asset_files

    def _return(self, msg, type='INFO'):
        """
        :param msg: 报告给用户的信息
        :param type: 信息/警告/错误弹窗
        :return: {'CANCELLED'}/{'FINISHED'}
        """

        self.report({type}, msg)
        if type == 'INFO':
            return {"FINISHED"}
        else:
            return {"CANCELLED"}

    def get_data(self, data_lib, name):
        """

        :param data_lib: 数据类型 str
        :param name: 数据名字
        :return:
        """
        data_lib = getattr(bpy.data, data_lib)
        data = data_lib.get(name)
        if not data:
            data_lib.new(name=name)

        return data

    def execute(self, context):
        match_obj = get_local_selected_assets(context)
        selected_mat = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        if len(selected_mat) == 0:
            self._return(msg='请选择一个材质资产', type='WARNING')

        # 创建集合
        tmp_coll = bpy.data.collections[
            'tmp_mathp'] if 'tmp_mathp' in bpy.data.collections else bpy.data.collections.new(
            'tmp_mathp')
        if 'tmp_mathp' not in context.scene.collection.children:
            context.scene.collection.children.link(tmp_coll)
        # 创建物体
        tmp_mesh = bpy.data.meshes['tmp_mathp'] if 'tmp_mathp' in bpy.data.meshes else bpy.data.meshes.new(
            'tmp_mathp')
        tmp_mesh.from_pydata([], [], [])
        tmp_mesh.update()

        tmp_obj = bpy.data.objects['tmp_mathp'] if 'tmp_mathp' in bpy.data.objects else bpy.data.objects.new(
            'tmp_mathp', tmp_mesh)
        if 'tmp_mathp' not in tmp_coll.objects:
            tmp_coll.objects.link(tmp_obj)
        # 设置激活项和材质
        context.view_layer.objects.active = tmp_obj
        tmp_obj.active_material = selected_mat[0]

        # 设置鼠标位置，以便弹窗出现在正中央
        w = context.window
        w_center_x, w_center_y = w.width / 2, w.height / 2
        w.cursor_warp(int(w_center_x), int(w_center_y))
        # 弹窗
        pop_up_window(area_type='NODE_EDITOR', ui_type='ShaderNodeTree')

        return {'FINISHED'}


class MATHP_OT_update_mat_pv(Operator):
    """Update Material Asset Preview"""
    bl_idname = 'mathp.update_mat_pv'
    bl_label = 'Update Material Preview'

    mat_name: StringProperty(name='Material Name')

    def execute(self, context):
        # 更新材质预览
        mat = bpy.data.materials.get(self.mat_name)
        if mat:
            mat.asset_generate_preview()

        return {'FINISHED'}


class MATHP_UI_update_mat_pv(GizmoGroup):
    """use_tooltip"""
    bl_idname = "MATHP_UI_update_mat_pv"
    bl_label = "Update Material Preview"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'WINDOW'
    bl_options = {'PERSISTENT', 'SCALE'}

    @classmethod
    def poll(cls, context):
        if context.area.type == 'NODE_EDITOR' and context.area.ui_type == 'ShaderNodeTree':
            return hasattr(context, 'material') and context.material.asset_data is not None

    def draw_prepare(self, context):
        region = context.region

        self.foo_gizmo.matrix_basis[0][3] = region.width - 40
        self.foo_gizmo.matrix_basis[1][3] = 40
        self.foo_gizmo.scale_basis = (80 * 0.35) / 2

    def setup(self, context):
        gz = self.gizmos.new("GIZMO_GT_button_2d")
        gz.icon = 'FILE_REFRESH'
        gz.draw_options = {'BACKDROP', 'OUTLINE'}
        gz.use_tooltip = True
        gz.alpha = 0
        gz.color_highlight = 0.8, 0.8, 0.8
        gz.alpha_highlight = 0.2

        gz.scale_basis = (80 * 0.35) / 2  # Same as buttons defined in C

        props = gz.target_set_operator("mathp.update_mat_pv")
        props.mat_name = context.material.name

        self.foo_gizmo = gz


def register():
    bpy.utils.register_class(MATHP_OT_edit_material_asset)
    bpy.utils.register_class(MATHP_OT_update_mat_pv)
    bpy.utils.register_class(MATHP_UI_update_mat_pv)


def unregister():
    bpy.utils.unregister_class(MATHP_OT_edit_material_asset)
    bpy.utils.unregister_class(MATHP_OT_update_mat_pv)
    bpy.utils.unregister_class(MATHP_UI_update_mat_pv)
