from . import (
    op_edit_material_asset,
    op_tmp_asset,
    op_align_nodes,
    op_clear_unused_material,
    op_replace_mat
)

module_list = [
    op_edit_material_asset,
    op_clear_unused_material,
    op_replace_mat,
    op_tmp_asset,
    op_align_nodes,
]


def register():
    for mod in module_list:
        mod.register()


def unregister():
    for mod in module_list:
        mod.unregister()
