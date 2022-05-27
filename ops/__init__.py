from . import op_edit_material_asset,op_tmp_asset

def register():
    op_edit_material_asset.register()
    op_tmp_asset.register()

def unregister():
    op_edit_material_asset.unregister()
    op_tmp_asset.unregister()

