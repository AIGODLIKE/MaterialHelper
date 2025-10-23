import bpy

from .poll import AssetPoll


class MATHP_OT_refresh_asset_preview(bpy.types.Operator, AssetPoll):
    bl_idname = "mathp.refresh_asset_preview"
    bl_label = "Refresh Preview"

    @classmethod
    def poll(cls, context):
        from ...utils import get_local_selected_assets
        if hasattr(context, "active_file") and super().poll(context):
            return context.active_file and get_local_selected_assets(context)
        return False

    def execute(self, context):
        from ...utils import get_local_selected_assets
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            mat.asset_generate_preview()

        return {"FINISHED"}
