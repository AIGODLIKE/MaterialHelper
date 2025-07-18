import bpy

from . import asset
from .add_material import MATHP_OT_add_material
from .align_nodes import MATHP_OT_move_dependence, MATHP_OT_align_dependence
from .clear_unused_material import ClearUnusedMaterial
from .replace_mat import MATHP_OT_replace_mat
from .select_material import MATHP_OT_select_material_obj

module_list = [
    asset,
    # tmp_asset,
]

class_list = [
    ClearUnusedMaterial,
    MATHP_OT_move_dependence,
    MATHP_OT_align_dependence,
    MATHP_OT_replace_mat,
    MATHP_OT_add_material,
    MATHP_OT_select_material_obj,
]

register_class, unregister_class = bpy.utils.register_classes_factory(class_list)


def register():
    register_class()
    for mod in module_list:
        mod.register()


def unregister():
    unregister_class()
    for mod in module_list:
        mod.unregister()
