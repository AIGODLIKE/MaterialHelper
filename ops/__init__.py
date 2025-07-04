from . import (
    edit_material_asset,
    tmp_asset,
    align_nodes,
    clear_unused_material,
    replace_mat
)

module_list = [
    edit_material_asset,
    clear_unused_material,
    replace_mat,
    tmp_asset,
    align_nodes,
]


def register():
    for mod in module_list:
        mod.register()


def unregister():
    for mod in module_list:
        mod.unregister()
