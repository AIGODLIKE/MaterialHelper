import bpy


class SetTrueAsset(bpy.types.Operator):
    """Apply Selected as True Assets"""
    bl_idname = "mathp.set_true_asset"
    bl_label = "Apply as Asset"
    bl_description = "Convert temporary assets into regular assets"

    @classmethod
    def poll(cls, context):
        from ...utils import get_local_selected_assets, MATERIAL_HELPER_ASSET_TAG
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]
        for mat in selected_mats:
            if MATERIAL_HELPER_ASSET_TAG in mat.asset_data.tags:
                return True
        return False

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        from ...utils import get_local_selected_assets, MATERIAL_HELPER_ASSET_TAG, tag_redraw
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            if MATERIAL_HELPER_ASSET_TAG in mat.asset_data.tags:
                tag = mat.asset_data.tags[MATERIAL_HELPER_ASSET_TAG]
                mat.asset_data.tags.remove(tag)
                self.report({"INFO"},
                            bpy.app.translations.pgettext_iface("{} is set as True Asset").format(mat.name))
        tag_redraw()
        return {"FINISHED"}
