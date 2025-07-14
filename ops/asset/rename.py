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

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        from ...utils import get_local_selected_assets
        active = get_local_selected_assets(context)[0]

        layout = self.layout
        layout.separator()
        layout.label(text="Name")
        if isinstance(active, bpy.types.Material):
            icon = "MATERIAL"
        elif isinstance(active, bpy.types.Object):
            icon = "OBJECT_DATA"
        elif isinstance(active, bpy.types.Collection):
            icon = "GROUP"
        elif isinstance(active, bpy.types.World):
            icon = "WORLD"
        else:
            icon = "ASSET_MANAGER"

        layout.prop(active, "name", text="", icon=icon)
        layout.separator()

    def execute(self, context):
        return {"FINISHED"}
