

class MATHP_OT_delete_asset(SelectedAsset, bpy.types.Operator):
    """Delete Selected Materials"""
    bl_idname = "mathp.delete_asset"
    bl_label = "Delete"
    bl_options = {"UNDO"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            bpy.data.materials.remove(mat)

        bpy.ops.asset.library_refresh()

        return {"FINISHED"}
