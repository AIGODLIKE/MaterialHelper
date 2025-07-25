import bpy

from bpy_extras.asset_utils import AssetMetaDataPanel


class MATERIAL_ASSET_PT_Header(AssetMetaDataPanel, bpy.types.Panel):
    bl_label = "Material Asset"

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'selected_assets') and context.selected_assets

    def draw(self, context):
        layout = self.layout
        layout.label(text="Edit Material")
        layout.label(text=f"id :{getattr(context, 'id', None)}")
        layout.label(text=f"id :{bpy.data.materials['Material']}")


def register():
    bpy.utils.register_class(MATERIAL_ASSET_PT_Header)


def unregister():
    bpy.utils.unregister_class(MATERIAL_ASSET_PT_Header)
