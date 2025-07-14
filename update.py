import bpy

from bpy.app.handlers import persistent

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


@persistent
def depsgraph_update_post(scene, depsgraph):
    # print("depsgraph_update_post", scene, depsgraph)
    ...


@persistent
def depsgraph_update_pre(scene, depsgraph):
    # print("depsgraph_update_pre", scene, depsgraph)
    ...


def register():
    load_subscribe()

    bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_post)
    bpy.app.handlers.depsgraph_update_pre.append(depsgraph_update_pre)


def unregister():
    bpy.msgbus.clear_by_owner(owner)

    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_post)
    bpy.app.handlers.depsgraph_update_pre.remove(depsgraph_update_pre)
