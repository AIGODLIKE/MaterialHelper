from . import ops, preferences, keymaps, ui, src, update

module_list = [
    src,
    ops,
    keymaps,
    update,
    preferences,

    ui,
]


def register():
    for mod in module_list:
        mod.register()


def unregister():
    for mod in module_list:
        mod.unregister()
