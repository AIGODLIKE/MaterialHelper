

class MATHP_OT_refresh_asset_pv(SelectedAsset, bpy.types.Operator):
    bl_idname = "mathp.refresh_asset_pv"
    bl_label = "Refresh Preview"

    @classmethod
    def poll(cls, context):
        if hasattr(context, "active_file"):
            return context.active_file and get_local_selected_assets(context)

    def execute(self, context):
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            mat.asset_generate_preview()

        return {"FINISHED"}

