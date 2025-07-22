from bpy_extras import asset_utils

from . import is_sync, sync_lock
from ..debug import DEBUG_SYNC
from ..utils import get_pref


def select_objects_to_material(context) -> None:
    if sync_lock():
        return

    pref = get_pref()
    if pref.sync_select is False:
        return
    elif not hasattr(context, "object"):
        return
    elif context.object is None:
        return
    elif context.object.type not in {"MESH", "CURVE", "FONT", "META", "VOLUME", "GPENCIL", "SURFACE"}:
        return
    elif len(context.object.material_slots) == 0:
        return
    # 获取面板
    asset_area = None
    for area in context.window.screen.areas:
        if area.type == "FILE_BROWSER" and area.ui_type == "ASSETS":
            asset_area = area
            break

    if asset_area is None:
        return

    # 获取材质
    materials_list = []

    for mat_slot in context.object.material_slots:
        materials_list.append(mat_slot.material)

    try:
        asset_area.spaces[0].deselect_all()  # window上有bug
        # 激活材质
        space_data = [a for a in asset_area.spaces if a.type == "FILE_BROWSER"][0]
        assert asset_utils.SpaceAssetInfo.is_asset_browser(space_data)

        if context.object.select_get():
            for mat in materials_list:
                space_data.activate_asset_by_id(mat, deferred=False)


    except Exception as e:
        print(e)
    if DEBUG_SYNC:
        print("select_objects_to_material", is_sync, context.object.name)
