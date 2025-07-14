import bpy



class ClearUnusedMaterial(bpy.types.Operator):
    bl_label = "Clear Unused Material"
    bl_idname = "mathp.clear_unused_material"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        from ..utils import MATERIAL_HELPER_ASSET_UUID, MATERIAL_HELPER_ASSET_TAG,tag_redraw

        for mat in bpy.data.materials:
            if not mat.asset_data:
                continue
            if MATERIAL_HELPER_ASSET_TAG in mat.asset_data.tags:
                mat.asset_clear()
            if mat.users == 0:
                bpy.data.materials.remove(mat)
            else:
                mat.asset_mark()
                mat.asset_generate_preview()
                mat.asset_data.tags.new(MATERIAL_HELPER_ASSET_TAG)
                if mat.asset_data.catalog_id != MATERIAL_HELPER_ASSET_UUID:
                    mat.asset_data.catalog_id = MATERIAL_HELPER_ASSET_UUID

        tag_redraw()

        return {"FINISHED"}
