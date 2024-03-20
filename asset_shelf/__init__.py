from . import gui, ops, keymaps

import threading


def register():
    gui.register()
    ops.register()
    keymaps.register()


def unregister():
    keymaps.unregister()
    ops.unregister()
    gui.unregister()
