import bpy

from .poll import AssetPoll


class MATHP_OT_rename_asset(bpy.types.Operator, AssetPoll):
    """Rename Active Item"""
    bl_idname = "mathp.rename_asset"
    bl_label = "Rename"
    bl_options = {"UNDO", "REGISTER"}

    rename_list = []

    @classmethod
    def poll(cls, context):
        from ...utils import get_local_selected_assets
        if hasattr(context, "active_file") and super().poll(context):
            return context.active_file and get_local_selected_assets(context)
        return False

    def invoke(self, context, event):
        from ...utils import get_local_selected_assets
        self.rename_list = get_local_selected_assets(context)
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        layout = self.layout
        column = layout.column(align=True)
        column.separator()
        column.label(text="Name")

        for asset in self.rename_list:
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
