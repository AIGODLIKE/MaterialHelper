from . import ops, preferences, keymaps, ui, src

module_list = [
    src,
    ops,
    keymaps,
    preferences,

    ui,
]


def register():
    for mod in module_list:
        mod.register()


def unregister():
    for mod in module_list:
        mod.unregister()
