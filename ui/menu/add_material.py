import bpy

from ...ops.add_material import MATHP_OT_add_material


class AddMaterialMenu(bpy.types.Menu):
    bl_label = "Add Material"
    bl_idname = "MATERIAL_HELPER_MT_add_material_menu"

    def draw(self, context):
        from ...src.material import material_list
        from ...utils import get_icon
        layout = self.layout

        layout.separator()

        for name, file_path in material_list.items():
            layout.operator(
                MATHP_OT_add_material.bl_idname,
                icon_value=get_icon(name),
                text=name.title()).file_path = file_path

        layout.separator()




