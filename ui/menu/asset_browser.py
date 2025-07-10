import bpy

from ...ops.clear_unused_material import ClearUnusedMaterial


class AssetBrowserMenu(bpy.types.Menu):
    bl_label = "Material Helper"
    bl_idname = "MATERIAL_HELPER_MT_asset_browser_menu"

    def draw(self, context):
        layout = self.layout

        layout.separator()

        layout.operator(ClearUnusedMaterial.bl_idname, icon="X")

        layout.separator()

        layout.operator("mathp.add_material", icon="ADD")
        layout.operator("mathp.duplicate_asset")
        layout.operator("mathp.rename_asset")
        layout.operator("mathp.replace_mat")
        layout.operator("mathp.delete_asset")

        layout.separator()

        layout.operator("mathp.set_true_asset", icon="ASSET_MANAGER")
