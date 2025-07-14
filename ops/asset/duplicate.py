
class MATHP_OT_duplicate_asset(SelectedAsset, bpy.types.Operator):
    """Duplicate Active Item"""
    bl_idname = "mathp.duplicate_asset"
    bl_label = "Duplicate"
    bl_options = {"UNDO"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            mat.copy()

        for mat in selected_mats:
            context.space_data.activate_asset_by_id(mat)

        return {"FINISHED"}
