from . import is_sync, sync_lock
from ..debug import DEBUG_SYNC

cache_len = {}


def select_material_to_object(context):
    global cache_len
    if sync_lock():
        return
    if getattr(context, "selected_assets", None) is None:
        return
    area_hash = hash(context.area)
    sl = len(context.selected_assets)

    last_asset = context.selected_assets[-1] if sl != 0 else None

    value = sl, hash(last_asset)
    if area_hash in cache_len:
        last_sl, last_asset_hash = cache_len[area_hash]
        if hash(last_asset) == last_asset_hash:
            return
    cache_len[area_hash] = value

    if sl == 1:
        material = last_asset.local_id
        id_type = last_asset.id_type
        if id_type == "MATERIAL":
            if DEBUG_SYNC:
                print("select_material_to_object", is_sync, material)
            for obj in context.scene.objects:
                if obj.type == "MESH" and not obj.hide_get() and not obj.hide_viewport:
                    is_select = material in obj.data.materials[:]
                    obj.select_set(is_select)
