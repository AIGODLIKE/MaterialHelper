import bpy


class MaterialPickerByAsset(bpy.types.Operator):
    bl_idname = "mathp.from_asset_picker_material"
    bl_label = "Picker material(Material Helper)"

    @classmethod
    def poll(cls, context):
        if not hasattr(context, "selected_assets"):
            return False
        if len(context.selected_assets) == 0:
            return False
        if not isinstance(context.selected_assets[0].local_id, bpy.types.Material):
            return False
        return True

    def execute(self, context):
        from ...utils import get_local_selected_assets
        material_helper_property = context.scene.material_helper_property
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]
        for asset in selected_mats:
            material_helper_property.try_picker_material(asset)
        return {"FINISHED"}
