import bpy

node_idnames = {

    'GeometryNodeReplaceMaterial',
    'GeometryNodeSetMaterial',
    'GeometryNodeMaterialSelection'
}

from .op_tmp_asset import update_tmp_asset
from .op_edit_material_asset import tag_redraw, SaveUpdate
from .functions import _uuid,C_TMP_ASSET_TAG


class MATHP_OT_clear_unused_material(bpy.types.Operator):
    bl_label = "Clear Unused Material"
    bl_idname = "mathp.clear_unused_material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for mat in bpy.data.materials:
            if C_TMP_ASSET_TAG in mat.asset_data.tags:
                mat.asset_clear()
            if mat.users == 0:
                bpy.data.materials.remove(mat)
            else:
                mat.asset_mark()
                mat.asset_generate_preview()
                mat.asset_data.tags.new(C_TMP_ASSET_TAG)
                if mat.asset_data.catalog_id != _uuid:
                    mat.asset_data.catalog_id = _uuid

        tag_redraw()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MATHP_OT_clear_unused_material)


def unregister():
    bpy.utils.unregister_class(MATHP_OT_clear_unused_material)
