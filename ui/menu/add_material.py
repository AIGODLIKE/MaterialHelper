import bpy

from ...ops.add_material import MATHP_OT_add_material


class AddMaterialMenu(bpy.types.Menu):
    bl_label = "Add Material"
    bl_idname = "MATERIAL_HELPER_MT_add_material_menu"

    def draw(self, context):
        layout = self.layout

        layout.separator()

        layout.operator(MATHP_OT_add_material.bl_idname, icon="X")

        layout.separator()

        layout.operator("mathp.add_material", icon="ADD")
        layout.operator("mathp.duplicate_asset")
        layout.operator("mathp.rename_asset")
        layout.operator("mathp.replace_mat")
        layout.operator("mathp.delete_asset")

        layout.separator()

        layout.operator("mathp.set_true_asset", icon="ASSET_MANAGER")
