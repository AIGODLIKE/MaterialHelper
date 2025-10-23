import bpy

from .asset import MATERIAL_ASSET_PT_Header
from .material import MaterialPanel
from .node import MATHP_PT_Node_edit_Panel, MATERIAL_PT_Node_tool_Panel

register_class, unregister_class = bpy.utils.register_classes_factory([
    MATERIAL_ASSET_PT_Header,
    MATHP_PT_Node_edit_Panel,
    MATERIAL_PT_Node_tool_Panel,
    MaterialPanel,
])


def register():
    register_class()


def unregister():
    unregister_class()
