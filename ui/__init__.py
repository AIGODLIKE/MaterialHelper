import bpy

from . import panel, menu
from ..ops.tmp_asset import MATHP_OT_refresh_asset_pv, MATHP_OT_select_material_obj


def draw_asset_browser(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.menu('MATHP_MT_asset_browser_menu')
    row.separator()
    row.prop(context.scene, 'mathp_update_mat', toggle=True, icon='FILE_REFRESH')
    row.prop(context.window_manager, 'mathp_update_active_obj_mats', toggle=True, icon='UV_SYNC_SELECT')
    row.separator()
    row.operator(MATHP_OT_refresh_asset_pv.bl_idname, icon='FILE_REFRESH')
    row.operator(MATHP_OT_select_material_obj.bl_idname, icon='RESTRICT_SELECT_OFF')
    row.operator('mathp.edit_material_asset', icon='NODETREE')
    row.operator('mathp.replace_mat', icon='CON_TRANSLIKE')
    row.operator('mathp.clear_unused_material', icon='NODE_MATERIAL')


def draw_context_menu(self, context):
    if not hasattr(context, 'selected_assets'): return
    if len(context.selected_assets) == 0: return
    if not isinstance(context.selected_assets[0].local_id, bpy.types.Material): return

    layout = self.layout
    layout.operator('mathp.duplicate_asset')
    layout.operator('mathp.delete_asset')
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator('mathp.replace_mat')
    layout.separator()


def register():
    panel.register()
    menu.register()

    bpy.types.ASSETBROWSER_MT_editor_menus.append(draw_asset_browser)
    bpy.types.ASSETBROWSER_MT_context_menu.prepend(draw_context_menu)

def unregister():
    panel.unregister()
    menu.unregister()

    bpy.types.ASSETBROWSER_MT_editor_menus.remove(draw_asset_browser)
    bpy.types.ASSETBROWSER_MT_context_menu.remove(draw_context_menu)