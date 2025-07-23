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
