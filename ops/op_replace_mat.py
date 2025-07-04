import bpy

from .op_tmp_asset import get_local_selected_assets


class MATHP_OT_replace_mat(bpy.types.Operator):
    bl_label = "Replace Selected Material to..."
    bl_idname = "mathp.replace_mat"
    bl_property = 'enum_mats'
    bl_options = {'REGISTER', 'UNDO'}

    _enum_mats = []  # store

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'selected_assets') and context.selected_assets

    def get_mats(self, context) -> list:
        enum_mats = MATHP_OT_replace_mat._enum_mats
        enum_mats.clear()

        for i, m in enumerate(bpy.data.materials):
            enum_mats.append((m.name, m.name, '', m.preview.icon_id, i))
        return enum_mats

    enum_mats: bpy.props.EnumProperty(
        name="Material",
        items=get_mats,
    )

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

    def execute(self, context):
        match_obj = get_local_selected_assets(context)
        selected_mat = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        if not selected_mat:
            return self._return(msg='请选择一个本地材质资产', type='WARNING')
        # print(selected_mat)
        selected_mat[0].user_remap(bpy.data.materials[self.enum_mats])

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MATHP_OT_replace_mat)


def unregister():
    bpy.utils.unregister_class(MATHP_OT_replace_mat)
