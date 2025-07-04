import bpy

owner = object()


def update_windows(*args):
    print("update_windows", args)


def load_subscribe():
    print("load_subscribe")
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.WindowManager, 'windows'),
        owner=owner,
        args=(),
        notify=update_windows,
        options={"PERSISTENT"}
    )


def register():
    load_subscribe()


def unregister():
    bpy.msgbus.clear_by_owner(owner)
