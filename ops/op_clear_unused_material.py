import bpy

node_idnames = {

    'GeometryNodeReplaceMaterial',
    'GeometryNodeSetMaterial',
    'GeometryNodeMaterialSelection'
}

from .op_tmp_asset import C_TMP_ASSET_TAG
from .op_edit_material_asset import tag_redraw, SaveUpdate


class MATHP_OT_clear_unused_material(bpy.types.Operator):
    bl_label = "Clear Unused Material"
    bl_idname = "mathp.clear_unused_material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for mat in bpy.data.materials:
            if mat.asset_data is None: continue

            if C_TMP_ASSET_TAG in mat.asset_data.tags:
                mat.asset_clear()

        with SaveUpdate():
            for mat in bpy.data.materials:
                if mat.users == 0:
                    mat.user_clear()
                    bpy.data.materials.remove(mat)

        tag_redraw()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MATHP_OT_clear_unused_material)

def unregister():
    bpy.utils.unregister_class(MATHP_OT_clear_unused_material)