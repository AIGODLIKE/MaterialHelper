import bpy
from bpy.app.handlers import persistent

from .sync.material_to_asset import AssetSync
from .sync.select_objects_to_material import select_objects_to_material

owner = object()


def switch_object():
    from .debug import DEBUG_HANDLER
    if DEBUG_HANDLER:
        print("switch_object")
    select_objects_to_material(bpy.context)


def load_subscribe():
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, 'active'),
        owner=owner,
        args=(),
        notify=switch_object,
        options={"PERSISTENT"}
    )


@persistent
def save_post(file_path):
    from .debug import DEBUG_HANDLER
    if DEBUG_HANDLER:
        print("save_post", file_path)
    AssetSync.sync()


@persistent
def load_post(file_path):
    from .debug import DEBUG_HANDLER
    if DEBUG_HANDLER:
        print("load_post", file_path)
    load_subscribe()
    from .utils.window import PreviewMaterialWindow
    PreviewMaterialWindow.clear_temp_preview_data()
    AssetSync.sync()


def register():
    bpy.app.handlers.load_post.append(load_post)
    bpy.app.handlers.save_post.append(save_post)


def unregister():
    bpy.msgbus.clear_by_owner(owner)

    bpy.app.handlers.load_post.remove(load_post)
    bpy.app.handlers.save_post.remove(save_post)
