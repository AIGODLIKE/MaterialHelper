import bpy

from .poll import AssetPoll


class MATHP_OT_duplicate_asset(bpy.types.Operator, AssetPoll):
    """Duplicate Active Item"""
    bl_idname = "mathp.duplicate_asset"
    bl_label = "Duplicate"
    bl_options = {"UNDO"}

    def execute(self, context):
        from ...utils import get_local_selected_assets
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            cp = mat.copy()
            cp.asset_mark()
            for tag in mat.asset_data.tags:
                cp.asset_data.tags.new(tag.name)
            cp.asset_data.catalog_id = mat.asset_data.catalog_id

        for mat in selected_mats:
            context.space_data.activate_asset_by_id(mat)
        return {"FINISHED"}
