import bpy


def get_mats(self, context) -> list:
    enum_mats = []

    for i, m in enumerate(bpy.data.materials):
        enum_mats.append((m.name, m.name, '', m.preview.icon_id, i))
    return enum_mats


class MATHP_OT_replace_mat(bpy.types.Operator):
    bl_label = "Replace Material"
    bl_idname = "mathp.replace_mat"
    bl_property = 'enum_mats'
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        return hasattr(context, 'selected_assets') and context.selected_assets

    enum_mats: bpy.props.EnumProperty(
        name="Material",
        items=get_mats,
    )

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

    def execute(self, context):
        from ..utils import get_local_selected_assets
        match_obj = get_local_selected_assets(context)
        selected_mat = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        if not selected_mat:
            self.report({"WARNING"}, '请选择一个本地材质资产')
            return {"CANCELLED"}
        selected_mat[0].user_remap(bpy.data.materials[self.enum_mats])
        return {'FINISHED'}
