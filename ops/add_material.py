import bpy


class MATHP_OT_add_material(bpy.types.Operator):
    """Add Material"""
    bl_idname = "mathp.add_material"
    bl_label = "Add Material"
    bl_options = {"REGISTER", "UNDO"}

    file_path: bpy.props.StringProperty(subtype="FILE_PATH")
    dep_class = []  # 动态ops

    @classmethod
    def poll(cls, context):
        return hasattr(context, "selected_assets")

    def execute(self, context):
        from ..utils.property import import_material
        self.material = material = import_material(self.file_path)
        material.asset_mark()
        bpy.ops.asset.library_refresh()
        material.asset_generate_preview()
        context.area.spaces[0].activate_asset_by_id(material)
        context.area.tag_redraw()
        bpy.ops.asset.library_refresh()
        return {"FINISHED"}
