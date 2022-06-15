bl_info = {
    "name": "Material Helper",
    "author": "幻之境科技,(开发:Atticus)",
    "version": (0, 1),
    "blender": (3, 0, 0),
    "location": "资产管理器",
    "description": "",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "wiki_url": "",
    "category": "Material"
}

__ADDON_NAME__ = __name__

from . import ops, prefs, ui, localdb


def register():
    ops.register()
    prefs.register()
    ui.register()
    localdb.register()


def unregister():
    ops.unregister()
    prefs.unregister()
    ui.unregister()
    localdb.unregister()


if __name__ == "__main__":
    register()
