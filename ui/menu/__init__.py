import bpy
from .asset_browser import AssetBrowserMenu


def register():
    bpy.utils.register_class(AssetBrowserMenu)


def unregister():
    bpy.utils.unregister_class(AssetBrowserMenu)
