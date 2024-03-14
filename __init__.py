bl_info = {
    "name": "Material Helper 材质助手",
    "author": "AIGODLIKE社区, Atticus",
    "version": (1, 1, 2),
    "blender": (4, 0, 0),
    "location": "资产管理器>顶部菜单>材质助手",
    "description": "将本地资产管理器作为你创造强大材质的地方吧",
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
