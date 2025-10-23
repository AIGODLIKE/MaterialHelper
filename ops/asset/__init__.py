import bpy

from .delete import MATHP_OT_delete_asset
from .duplicate import MATHP_OT_duplicate_asset
from .edit_material import EditMaterial
from .refresh_asset_preview import MATHP_OT_refresh_asset_preview
from .apply_asset import ApplyAsset
from .rename import MATHP_OT_rename_asset
from .add_material import MATHP_OT_add_material

class_list = [
    MATHP_OT_duplicate_asset,
    MATHP_OT_delete_asset,
    MATHP_OT_refresh_asset_preview,
    MATHP_OT_rename_asset,
    MATHP_OT_add_material,
    EditMaterial,
    ApplyAsset,
]

register_class, unregister_class = bpy.utils.register_classes_factory(class_list)


def register():
    register_class()


def unregister():
    unregister_class()
