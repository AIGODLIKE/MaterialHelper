import bpy


class Material:
    preview_render_type: bpy.props.EnumProperty(
        name="Preview Render Type",
        items=[
            ("NONE", "Follow Material", ""),
            ("FLAT", "Flat", ""),
            ("SPHERE", "Sphere", ""),
            ("CUBE", "Cube", ""),
            ("HAIR", "Hair", ""),
            ("SHADERBALL", "Shader Ball", ""),
            ("CLOTH", "Cloth", ""),
            ("FLUID", "Fluid", ""),
        ],
        default="SHADERBALL")
    shading_type: bpy.props.EnumProperty(
        name="Shading",
        items=[
            ("SOLID", "Solid", ""),
            ("MATERIAL", "Material", "", "SHADING_SOLID", 1),
            ("RENDERED", "Rendered", "", "SHADING_RENDERED", 2),
        ], default="MATERIAL")

    picker_material_preview_scale: bpy.props.FloatProperty(default=2, min=0.5, max=9, name="Preview Scale")
    picker_material_preview_bar_scale: bpy.props.FloatProperty(default=3, min=0.5, max=9, name="Bar Scale")
    picker_material_bottom_offset: bpy.props.IntProperty(default=20, name="Bottom Offset")
    picker_material_preview_bar_background_color: bpy.props.FloatVectorProperty(
        name="Background Color", subtype="COLOR", size=4, min=0, max=1, default=(.3, .3, .3, .5)
    )
    def draw_material(self, layout: bpy.types.UILayout):
        column = layout.column(align=True)
        column.prop(self, "picker_material_preview_scale")
        column.prop(self, "picker_material_preview_bar_scale")
        column.prop(self, "picker_material_bottom_offset")
        column.prop(self, "picker_material_preview_bar_background_color")
