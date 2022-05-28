from . import op_edit_material_asset,op_tmp_asset,op_align_nodes

def register():
    op_edit_material_asset.register()
    op_tmp_asset.register()
    op_align_nodes.register()

def unregister():
    op_edit_material_asset.unregister()
    op_tmp_asset.unregister()
    op_align_nodes.unregister()

