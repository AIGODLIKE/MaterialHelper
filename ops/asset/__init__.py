import bpy

from .duplicate import MATHP_OT_duplicate_asset

class_list = [
    MATHP_OT_duplicate_asset,
]

register_class, unregister_class = bpy.utils.register_classes_factory(class_list)


def register():
    register_class()


def unregister():
    unregister_class()
