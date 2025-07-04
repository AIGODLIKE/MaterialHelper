from . import ops, preferences, keymaps, ui, src, property

module_list = [
    property,
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
