from . import ops, preferences, keymaps, ui, src, property, update

module_list = [
    property,
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
