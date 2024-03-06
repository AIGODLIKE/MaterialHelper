from . import op_edit_material_asset, op_tmp_asset, op_align_nodes, op_category, op_clear_unused_material, \
    op_replace_mat


def register():
    op_edit_material_asset.register()
    op_clear_unused_material.register()
    op_replace_mat.register()
    op_tmp_asset.register()
    op_align_nodes.register()
    op_category.register()


def unregister():
    op_edit_material_asset.unregister()
    op_clear_unused_material.unregister()
    op_replace_mat.unregister()
    op_tmp_asset.unregister()
    op_align_nodes.unregister()
    op_category.unregister()
