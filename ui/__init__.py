import bpy

from . import panel, menu, header
from ..utils import get_pref


def draw_asset_browser(self, context):
    from .menu.asset_browser import AssetBrowserMenu
    from ..ops.select_material import MATHP_OT_select_material_obj
    pref = get_pref()

    args = {}
    if pref.show_text is False:
        args["text"] = ""
    layout = self.layout
    row = layout.row(align=False)
    row.separator(factor=3)
    row.menu(AssetBrowserMenu.bl_idname)
    ar = row.row(align=True)
    ar.prop(pref, "auto_update", toggle=True, icon="ASSET_MANAGER", **args)
    ar.prop(pref, "update_active_obj_materials", toggle=True, icon="VIS_SEL_11", **args)

    br = row.row(align=True)
    # br.separator()
    br.operator(MATHP_OT_select_material_obj.bl_idname, icon="RESTRICT_SELECT_OFF", **args)
    br.operator("mathp.replace_mat", icon="CON_TRANSLIKE", **args)


def draw_context_menu(self, context):
    from ..ops.asset.refresh_asset_preview import MATHP_OT_refresh_asset_preview

    if not hasattr(context, "selected_assets"):
        return
    if len(context.selected_assets) == 0:
        return
    if not isinstance(context.selected_assets[0].local_id, bpy.types.Material):
        return

    layout = self.layout
    layout.operator("mathp.edit_material_asset")
    layout.operator("mathp.duplicate_asset")
    layout.operator("mathp.delete_asset")
    layout.operator("mathp.replace_mat")
    layout.operator(MATHP_OT_refresh_asset_preview.bl_idname, icon="FILE_REFRESH")
    layout.separator()


def register():
    panel.register()
    menu.register()
    header.register()

    bpy.types.ASSETBROWSER_MT_editor_menus.append(draw_asset_browser)
    bpy.types.ASSETBROWSER_MT_context_menu.prepend(draw_context_menu)


def unregister():
    panel.unregister()
    menu.unregister()
    header.unregister()

    bpy.types.ASSETBROWSER_MT_editor_menus.remove(draw_asset_browser)
    bpy.types.ASSETBROWSER_MT_context_menu.remove(draw_context_menu)
