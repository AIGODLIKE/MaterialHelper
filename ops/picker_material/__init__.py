import bpy

from .assign_by_item import MaterialAssignByItem
from .assign_by_modal import MaterialAssignByModal
from .clear import MaterialClear
from .drag import MaterialDrag
from .picker import MaterialPicker
from .from_asset_picker_material import MaterialPickerByAsset

class_tuples = (
    MaterialDrag,
    MaterialAssignByItem,
    MaterialAssignByModal,
    MaterialClear,
    MaterialPicker,
    MaterialPickerByAsset,
)

register_class, unregister_class = bpy.utils.register_classes_factory(class_tuples)


def register():
    register_class()


def unregister():
    unregister_class()
