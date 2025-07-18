import bpy
from ..utils import MATERIAL_HELPER_ASSET_UUID, MATERIAL_HELPER_ASSET_TAG,get_pref

class AssetSync:

    @staticmethod
    def sync():
        pref = get_pref()
def remove_all_tmp_tags():
    for mat in bpy.data.materials:
        if mat.asset_data is None: continue
        for tag in mat.asset_data.tags:
            if tag.name == MATERIAL_HELPER_ASSET_TAG:
                mat.asset_data.tags.remove(tag)


class MATHP_OT_set_true_asset(SelectedAsset, bpy.types.Operator):
    """Apply Selected as True Assets"""
    bl_idname = "mathp.set_true_asset"
    bl_label = "Apply"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            if MATERIAL_HELPER_ASSET_TAG in mat.asset_data.tags:
                tag = mat.asset_data.tags[MATERIAL_HELPER_ASSET_TAG]
                mat.asset_data.tags.remove(tag)
                self.report({"INFO"}, bpy.app.translations.pgettext_iface("{} is set as True Asset").format(mat.name))
        tag_redraw()
        return {"FINISHED"}


def update_tmp_asset(scene, depsgraph):
    if scene.mathp_update_mat is False: return

    global G_MATERIAL_COUNT
    old_value = G_MATERIAL_COUNT

    if len(bpy.data.materials) != old_value:
        G_MATERIAL_COUNT = len(bpy.data.materials)
        bpy.ops.mathp.set_tmp_asset()


class MATHP_OT_set_tmp_asset(bpy.types.Operator):
    bl_idname = "mathp.set_tmp_asset"
    bl_label = "Set Temp Asset"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        for mat in bpy.data.materials:
            if mat.asset_data: continue
            if mat.is_grease_pencil: continue
            mat.asset_mark()
            mat.asset_generate_preview()
            mat.asset_data.tags.new(MATERIAL_HELPER_ASSET_TAG)

        tag_redraw()

        if bpy.data.filepath == "":
            return {"CANCELLED"}

        ensure_current_file_asset_cats()

        for mat in bpy.data.materials:
            if mat.asset_data is None: continue
            if MATERIAL_HELPER_ASSET_TAG in mat.asset_data.tags:
                if mat.asset_data.catalog_id != MATERIAL_HELPER_ASSET_UUID:
                    mat.asset_data.catalog_id = MATERIAL_HELPER_ASSET_UUID
        try:
            bpy.ops.asset.library_refresh()
        except Exception as e:
            print(e)

        return {"FINISHED"}


class MATHP_OT_clear_tmp_asset(bpy.types.Operator):
    bl_idname = "mathp.clear_tmp_asset"
    bl_label = "Clear Temp Asset"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        for mat in bpy.data.materials:
            if mat.asset_data is None: continue

            if MATERIAL_HELPER_ASSET_TAG in mat.asset_data.tags:
                mat.asset_clear()
        tag_redraw()
        return {"FINISHED"}
