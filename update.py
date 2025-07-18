import bpy

from bpy.app.handlers import persistent

owner = object()


def update_windows(*args):
    print("update_windows", args)


def load_subscribe():
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.WindowManager, 'windows'),
        owner=owner,
        args=(),
        notify=update_windows,
        options={"PERSISTENT"}
    )


@persistent
def load_post(file_path):
    from .utils.window import PreviewMaterialWindow
    PreviewMaterialWindow.clear_temp_preview_data()


def register():
    load_subscribe()

    bpy.app.handlers.load_post.append(load_post)


def unregister():
    bpy.msgbus.clear_by_owner(owner)

    bpy.app.handlers.load_post.remove(load_post)
