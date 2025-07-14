import bpy
from .asset_browser import AssetBrowserMenu
from .add_material import AddMaterialMenu

register_class, unregister_class = bpy.utils.register_classes_factory([
    AssetBrowserMenu,
    AddMaterialMenu,
])


def register():
    register_class()


def unregister():
    unregister_class()
