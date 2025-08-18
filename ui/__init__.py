import bpy

from . import panel, menu
from ..sync.select_material_to_object import select_material_to_object
from ..utils import get_pref
from ..utils.window import PreviewMaterialWindow


def draw_asset_browser(self, context):
    from .menu.asset_browser import AssetBrowserMenu
    from ..ops.asset.refresh_asset_preview import MATHP_OT_refresh_asset_preview
    pref = get_pref()

    args = {}
    if pref.show_text is False:
        args["text"] = ""
    layout = self.layout
    row = layout.row(align=False)
    row.separator(factor=3)
    row.menu(AssetBrowserMenu.bl_idname)
    sub_row = row.row(align=True)
    sub_row.prop(pref, "auto_update", toggle=True, icon="ASSET_MANAGER", **args)
    ss_row = sub_row.row(align=True)
    ss_row.enabled = pref.auto_update
    ss_row.prop(pref, "sync_select", toggle=True, icon="VIS_SEL_11", **args)

    sub_row = row.row(align=True)
    sub_row.operator("mathp.replace_mat", icon="CON_TRANSLIKE", **args)
    sub_row.operator(MATHP_OT_refresh_asset_preview.bl_idname, icon="FILE_REFRESH", **args)

    if pref.sync_select:
        select_material_to_object(context)


def draw_picker_by_asset(self, context):
    from ..ops.picker_material.from_asset_picker_material import MaterialPickerByAsset
    if not hasattr(context, "selected_assets"):
        return
    if len(context.selected_assets) == 0:
        return
    if not isinstance(context.selected_assets[0].local_id, bpy.types.Material):
        return

    layout = self.layout
    layout.operator_context = "INVOKE_DEFAULT"
    layout.operator(MaterialPickerByAsset.bl_idname, icon="ASSET_MANAGER")


def draw_context_menu(self, context):
    from ..ops.asset.refresh_asset_preview import MATHP_OT_refresh_asset_preview
    from ..ops.select_material import MATHP_OT_select_material_obj

    if not hasattr(context, "selected_assets"):
        return
    if len(context.selected_assets) == 0:
        return
    if not isinstance(context.selected_assets[0].local_id, bpy.types.Material):
        return

    layout = self.layout
    layout.operator_context = "INVOKE_DEFAULT"
    layout.operator("mathp.edit_material_asset")
    layout.operator("mathp.duplicate_asset")
    layout.operator("mathp.delete_asset")
    layout.operator("mathp.replace_mat")
    layout.operator("mathp.rename_asset")
    layout.operator("mathp.apply_asset")
    layout.operator(MATHP_OT_select_material_obj.bl_idname, icon="RESTRICT_SELECT_OFF")
    layout.operator(MATHP_OT_refresh_asset_preview.bl_idname, icon="FILE_REFRESH")

    draw_picker_by_asset(self, context)

    layout.separator()

def draw_node_header(self, context):
    if PreviewMaterialWindow.check_full_window(context.window):
        layout = self.layout
        row = layout.row(align=True)
        row.alert = True
        row.operator("wm.window_fullscreen_toggle", icon="DESKTOP", text="Switch window")
        row.operator("wm.window_close", icon="PANEL_CLOSE", text="Close Window")  # bug 直接关闭可能会闪退


def register():
    panel.register()
    menu.register()

    bpy.types.ASSETBROWSER_MT_editor_menus.append(draw_asset_browser)
    bpy.types.ASSETBROWSER_MT_context_menu.prepend(draw_context_menu)
    bpy.types.NODE_HT_header.append(draw_node_header)


def unregister():
    panel.unregister()
    menu.unregister()

    bpy.types.ASSETBROWSER_MT_editor_menus.remove(draw_asset_browser)
    bpy.types.ASSETBROWSER_MT_context_menu.remove(draw_context_menu)
    bpy.types.NODE_HT_header.remove(draw_node_header)
