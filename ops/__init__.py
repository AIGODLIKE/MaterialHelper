from . import op_edit_material_asset, op_tmp_asset, op_align_nodes, op_category


def register():
    op_edit_material_asset.register()
    op_tmp_asset.register()
    op_align_nodes.register()
    op_category.register()


def unregister():
    op_edit_material_asset.unregister()
    op_tmp_asset.unregister()
    op_align_nodes.unregister()
    op_category.unregister()
