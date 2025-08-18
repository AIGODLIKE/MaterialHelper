import bpy



class MaterialPanel(bpy.types.Panel):
    bl_idname = "MATERIAL_PT_Panel"
    bl_label = "Material board"

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Material"
    bl_options = set()

    @classmethod
    def poll(cls, context):
        return context.mode in ("OBJECT", "EDIT_MESH")

    def draw(self, context):
        layout = self.layout
        context.scene.material_helper_property.draw_picker_material(context, layout)

    def draw_header_preset(self, context):
        from ...ops.picker_material import MaterialPicker, MaterialClear
        layout = self.layout
        row = layout.row(align=True)
        row.operator(MaterialPicker.bl_idname, text="", icon="EYEDROPPER", emboss=False)
        layout.separator()
        layout.operator(MaterialClear.bl_idname, text="", icon="PANEL_CLOSE", emboss=False)
        layout.separator(factor=5)

def register():
    bpy.utils.register_class(MaterialPanel)


def unregister():
    bpy.utils.unregister_class(MaterialPanel)
