import bpy

from bpy_extras.asset_utils import AssetMetaDataPanel


class Material_Helper_HT_Header(AssetMetaDataPanel, bpy.types.Panel):
    # bl_space_type = 'FILE_BROWSER'
    bl_label = "AAA"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Edit Material")
        layout.label(text=f"id :{getattr(context, 'id', None)}")
        layout.label(text=f"id :{bpy.data.materials['Material']}")


def register():
    bpy.utils.register_class(Material_Helper_HT_Header)


def unregister():
    bpy.utils.unregister_class(Material_Helper_HT_Header)
