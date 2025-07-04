from . import panel, menu


def register():
    panel.register()
    menu.register()


def unregister():
    panel.unregister()
    menu.unregister()
