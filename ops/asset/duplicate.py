import bpy


class MATHP_OT_duplicate_asset(bpy.types.Operator):
    """Duplicate Active Item"""
    bl_idname = "mathp.duplicate_asset"
    bl_label = "Duplicate"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'selected_assets') and context.selected_assets

    def execute(self, context):
        from ...utils import get_local_selected_assets
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            cp = mat.copy()
            cp.asset_mark()

        for mat in selected_mats:
            context.space_data.activate_asset_by_id(mat)
        return {"FINISHED"}
