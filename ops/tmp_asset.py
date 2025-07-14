import os
from pathlib import Path

import bpy
from bpy.utils import previews
from bpy_extras import asset_utils

from ops.asset.edit_material_asset import get_local_selected_assets, tag_redraw
from .functions import ensure_current_file_asset_cats, SelectedAsset
from ..utils import MATERIAL_HELPER_ASSET_UUID, MATERIAL_HELPER_ASSET_TAG

G_MATERIAL_COUNT = 0  # 材质数量，用于更新临时资产
G_ACTIVE_MATS_LIST = []  # 选中材质列表


class MATHP_OT_set_tmp_asset(bpy.types.Operator):
    bl_idname = "mathp.set_tmp_asset"
    bl_label = "Set Temp Asset"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        for mat in bpy.data.materials:
            if mat.asset_data: continue
            if mat.is_grease_pencil: continue
            mat.asset_mark()
            mat.asset_generate_preview()
            mat.asset_data.tags.new(MATERIAL_HELPER_ASSET_TAG)

        tag_redraw()

        if bpy.data.filepath == "":
            return {"CANCELLED"}

        ensure_current_file_asset_cats()

        for mat in bpy.data.materials:
            if mat.asset_data is None: continue
            if MATERIAL_HELPER_ASSET_TAG in mat.asset_data.tags:
                if mat.asset_data.catalog_id != MATERIAL_HELPER_ASSET_UUID:
                    mat.asset_data.catalog_id = MATERIAL_HELPER_ASSET_UUID
        try:
            bpy.ops.asset.library_refresh()
        except Exception as e:
            print(e)

        return {"FINISHED"}


class MATHP_OT_clear_tmp_asset(bpy.types.Operator):
    bl_idname = "mathp.clear_tmp_asset"
    bl_label = "Clear Temp Asset"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        for mat in bpy.data.materials:
            if mat.asset_data is None: continue

            if MATERIAL_HELPER_ASSET_TAG in mat.asset_data.tags:
                mat.asset_clear()

        tag_redraw()

        return {"FINISHED"}

class MATHP_OT_set_true_asset(SelectedAsset, bpy.types.Operator):
    """Apply Selected as True Assets"""
    bl_idname = "mathp.set_true_asset"
    bl_label = "Apply"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            if MATERIAL_HELPER_ASSET_TAG in mat.asset_data.tags:
                tag = mat.asset_data.tags[MATERIAL_HELPER_ASSET_TAG]
                mat.asset_data.tags.remove(tag)
                self.report({"INFO"}, bpy.app.translations.pgettext_iface("{} is set as True Asset").format(mat.name))

        tag_redraw()

        return {"FINISHED"}


# icon注册
G_PV_COLL = {}
G_MAT_ICON_ID = {}  # name:id


def register_icon():
    icon_dir = Path(__file__).parent.parent.joinpath("mat_lib")
    mats_icon = []

    for file in os.listdir(str(icon_dir)):
        if file.endswith(".png"):
            mats_icon.append(icon_dir.joinpath(file))
    # 注册
    pcoll = previews.new()

    for icon_path in mats_icon:
        pcoll.load(icon_path.name[:-4], str(icon_path), "IMAGE")
        G_MAT_ICON_ID[icon_path.name[:-4]] = pcoll.get(icon_path.name[:-4]).icon_id

    G_PV_COLL["mathp_icon"] = pcoll


def unregister_icon():
    # global G_PV_COLL, G_MAT_ICON_ID

    for pcoll in G_PV_COLL.values():
        previews.remove(pcoll)
    G_PV_COLL.clear()

    G_MAT_ICON_ID.clear()


from bpy.app.handlers import persistent


@persistent
def update_tmp_asset(scene, depsgraph):
    if scene.mathp_update_mat is False: return

    global G_MATERIAL_COUNT
    old_value = G_MATERIAL_COUNT

    if len(bpy.data.materials) != old_value:
        G_MATERIAL_COUNT = len(bpy.data.materials)
        bpy.ops.mathp.set_tmp_asset()


@persistent
def update_active_object_material(scene, depsgraph):
    wm = bpy.context.window_manager
    if scene.mathp_update_mat is False:
        return
    elif wm.mathp_update_active_obj_mats is False:
        return
    elif not hasattr(bpy.context, "object"):
        return
    elif bpy.context.object is None:
        return
    elif bpy.context.object.type not in {"MESH", "CURVE", "FONT", "META", "VOLUME", "GPENCIL", "SURFACE"}:
        return
    elif len(bpy.context.object.material_slots) == 0:
        return
    # 获取面板
    asset_area = None
    for area in bpy.context.window.screen.areas:
        if area.type == "FILE_BROWSER" and area.ui_type == "ASSETS":
            asset_area = area
            break

    if asset_area is None: return

    # 获取材质
    global G_ACTIVE_MATS_LIST
    G_ACTIVE_MATS_LIST.clear()

    for mat_slot in bpy.context.object.material_slots:
        G_ACTIVE_MATS_LIST.append(mat_slot.material)

    G_ACTIVE_MATS_LIST.reverse()

    try:
        asset_area.spaces[0].deselect_all()  # window上有bug
        # 激活材质
        space_data = asset_area.spaces[0]
        assert asset_utils.SpaceAssetInfo.is_asset_browser(space_data)

        if bpy.context.object.select_get():
            for mat in G_ACTIVE_MATS_LIST:
                space_data.activate_asset_by_id(mat, deferred=False)


    except Exception as e:
        print(e)


def update_user_control(self, context):
    if context.scene.mathp_update_mat is True:
        bpy.ops.mathp.set_tmp_asset()
    else:
        bpy.ops.mathp.clear_tmp_asset()


def remove_all_tmp_tags():
    for mat in bpy.data.materials:
        if mat.asset_data is None: continue
        for tag in mat.asset_data.tags:
            if tag.name == MATERIAL_HELPER_ASSET_TAG:
                mat.asset_data.tags.remove(tag)


classes = (
    MATHP_OT_set_tmp_asset,
    MATHP_OT_clear_tmp_asset,
    MATHP_OT_set_true_asset,
    MATHP_OT_delete_asset,
    MATHP_OT_duplicate_asset,
    MATHP_OT_rename_asset,
    MATHP_OT_add_material,
    MATHP_OT_refresh_asset_pv,
    MATHP_OT_select_material_obj,
)


# def register_later(lock, t):
#     # to prevent bug
#     import time
#     while not hasattr(bpy.context, "scene"):
#         time.sleep(5)
#     wm = bpy.context.window_manager
#     wm.mathp_update_active_obj_mats = True


def register():
    # register_icon()

    for cls in classes:
        bpy.utils.register_class(cls)
    # handle
    # ui

    # import threading
    # lock = threading.Lock()
    # lock_holder = threading.Thread(target=register_later, args=(lock, 5), name="Init_Scene2")
    # lock_holder.daemon = True
    # lock_holder.start()


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    remove_all_tmp_tags()
    # unregister_icon()
    # handle
