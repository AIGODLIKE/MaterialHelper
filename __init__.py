bl_info = {
    "name": "Material Helper 材质助手",
    "author": "AIGODLIKE社区, Atticus, 小萌新",
    "version": (1, 4, 2),
    "blender": (4, 5, 0),
    "location": "资产管理器>顶部菜单>材质助手",
    "description": "Make the local asset manager your place to create powerful materials",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "wiki_url": "",
    "category": "Material"
}

from . import register_module


def register():
    register_module.register()


def unregister():
    register_module.unregister()
