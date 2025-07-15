import bpy

from .duplicate import MATHP_OT_duplicate_asset
from .delete import MATHP_OT_delete_asset
from .refresh_asset import MATHP_OT_refresh_asset_preview
from .edit_material import EditMaterial

class_list = [
    MATHP_OT_duplicate_asset,
    MATHP_OT_delete_asset,
    MATHP_OT_refresh_asset_preview,
    EditMaterial,
]

register_class, unregister_class = bpy.utils.register_classes_factory(class_list)


def register():
    register_class()


def unregister():
    unregister_class()
