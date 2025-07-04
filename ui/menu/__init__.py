import bpy
from .asset_browser import MATHP_MT_asset_browser_menu


def register():
    bpy.utils.register_class(MATHP_MT_asset_browser_menu)


def unregister():
    bpy.utils.unregister_class(MATHP_MT_asset_browser_menu)
