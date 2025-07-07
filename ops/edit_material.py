import bpy

from ..utils import get_pref


class EditMaterial(bpy.types.Operator):
    bl_idname = 'mathp.edit_material_asset'
    bl_label = 'Edit Material Asset'

    @classmethod
    def poll(cls, context):
        return (hasattr(context, 'selected_assets') and context.selected_assets) or context.asset

    def execute(self, context):
        if self.material:
            selected_mat = [bpy.data.materials[self.material], ]
        else:
            match_obj = get_local_selected_assets(context)
            selected_mat = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

            if not selected_mat:
                return self._return(msg='请选择一个本地材质资产', type='WARNING')
            # print(selected_mat)

        # 创建集合
        tmp_coll = bpy.data.collections[
            'tmp_mathp'] if 'tmp_mathp' in bpy.data.collections else bpy.data.collections.new(
            'tmp_mathp')
        if 'tmp_mathp' not in context.scene.collection.children:
            context.scene.collection.children.link(tmp_coll)

        # 设置材质球/材质

        set_shader_ball_mat(selected_mat[0], tmp_coll)
        selected_mat[0].asset_generate_preview()

        # 设置鼠标位置，以便弹窗出现在正中央
        w = context.window
        w_center_x, w_center_y = w.width / 2, w.height / 2
        w.cursor_warp(int(w_center_x), int(w_center_y))
        # 弹窗
        pop_up_window(style=get_pref().window_style)

        return {'FINISHED'}
