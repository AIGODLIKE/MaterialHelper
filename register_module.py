from . import ops, preferences, keymaps, ui, src, update, property

module_list = [
    src,
    ops,
    keymaps,
    update,
    property,
    preferences,

    ui,
]


def register():
    for mod in module_list:
        mod.register()


def unregister():
    for mod in module_list:
        mod.unregister()
