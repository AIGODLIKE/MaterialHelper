from . import node, asset


def register():
    node.register()
    asset.register()


def unregister():
    node.unregister()
    asset.unregister()
