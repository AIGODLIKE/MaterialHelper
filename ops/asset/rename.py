import bpy


class MATHP_OT_rename_asset(bpy.types.Operator):
    """Rename Active Item"""
    bl_idname = "mathp.rename_asset"
    bl_label = "Rename"
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        from ...utils import get_local_selected_assets
        if hasattr(context, "active_file"):
            return context.active_file and get_local_selected_assets(context)
        return False

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        from ...utils import get_local_selected_assets
        layout = self.layout
        column = layout.column(align=True)
        column.separator()
        column.label(text="Name")
        asset = get_local_selected_assets(context)[0]
        if isinstance(asset, bpy.types.Material):
            icon = "MATERIAL"
        elif isinstance(asset, bpy.types.Object):
            icon = "OBJECT_DATA"
        elif isinstance(asset, bpy.types.Collection):
            icon = "GROUP"
        elif isinstance(asset, bpy.types.World):
            icon = "WORLD"
        else:
            icon = "ASSET_MANAGER"

        column.prop(asset, "name", text="", icon=icon)
        column.separator()

    def execute(self, context):
        return {"FINISHED"}
