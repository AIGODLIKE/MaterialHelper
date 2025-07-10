import bpy

from . import panel
from .menu.asset_browser import AssetBrowserMenu
from ..ops.tmp_asset import MATHP_OT_refresh_asset_pv, MATHP_OT_select_material_obj
from ..utils import get_pref


def draw_asset_browser(self, context):
    pref = get_pref()

    layout = self.layout
    row = layout.row(align=True)
    row.menu(AssetBrowserMenu.bl_idname)
    row.separator()
    row.prop(pref, 'auto_update', toggle=True, icon='FILE_REFRESH')
    row.prop(pref, 'update_active_obj_materials', toggle=True, icon='UV_SYNC_SELECT')
    row.separator()
    row.operator(MATHP_OT_refresh_asset_pv.bl_idname, icon='FILE_REFRESH')
    row.operator(MATHP_OT_select_material_obj.bl_idname, icon='RESTRICT_SELECT_OFF')
    row.operator('mathp.edit_material_asset', icon='NODETREE')
    row.operator('mathp.replace_mat', icon='CON_TRANSLIKE')
    row.operator('mathp.clear_unused_material', icon='NODE_MATERIAL')


def draw_context_menu(self, context):
    if not hasattr(context, 'selected_assets'):
        return
    if len(context.selected_assets) == 0:
        return
    if not isinstance(context.selected_assets[0].local_id, bpy.types.Material):
        return

    layout = self.layout
    layout.operator('mathp.duplicate_asset')
    layout.operator('mathp.delete_asset')
    layout.operator('mathp.replace_mat')
    layout.separator()


def register():
    panel.register()
    bpy.utils.register_class(AssetBrowserMenu)

    bpy.types.ASSETBROWSER_MT_editor_menus.append(draw_asset_browser)
    bpy.types.ASSETBROWSER_MT_context_menu.prepend(draw_context_menu)


def unregister():
    panel.unregister()
    bpy.utils.unregister_class(AssetBrowserMenu)

    bpy.types.ASSETBROWSER_MT_editor_menus.remove(draw_asset_browser)
    bpy.types.ASSETBROWSER_MT_context_menu.remove(draw_context_menu)
