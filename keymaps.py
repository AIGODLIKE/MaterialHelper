import bpy

addon_keymaps = []

KEYMAPS = {
    "File Browser": [
        {"idname": "mathp.edit_material_asset", "type": "LEFTMOUSE", "value": "DOUBLE_CLICK"},
        {"idname": "mathp.delete_asset", "type": "X", "value": "PRESS"},
        {"idname": "mathp.apply_asset", "type": "A", "value": "PRESS", "ctrl": True},
        {"idname": "mathp.duplicate_asset", "type": "D", "value": "PRESS", "shift": True},
        {"idname": "mathp.rename_asset", "type": "F2", "value": "PRESS"},
        {"idname": "wm.call_menu", "type": "A", "value": "PRESS","shift":True,
         "properties": {"name": "MATERIAL_HELPER_MT_add_material_menu"}},
    ],
    "Node Editor": [
        {"idname": "mathp.align_dependence", "type": "A", "value": "PRESS", "ctrl": True},
        {"idname": "mathp.move_dependence", "type": "D", "value": "PRESS"}
    ]
}


def get_keymap(keymap_name) -> "bpy.types.KeyMap":
    kc = bpy.context.window_manager.keyconfigs
    addon = kc.addon
    keymap = kc.default.keymaps.get(keymap_name, None)
    return addon.keymaps.new(
        keymap_name,
        space_type=keymap.space_type,
        region_type=keymap.region_type
    )


def register():
    wm = bpy.context.window_manager
    if not wm.keyconfigs.addon:
        return

    for keymap_name, keymap_items in KEYMAPS.items():
        km = get_keymap(keymap_name)
        for item in keymap_items:
            idname = item.get("idname")
            key_type = item.get("type")
            value = item.get("value")

            shift = item.get("shift", False)
            ctrl = item.get("ctrl", False)
            alt = item.get("alt", False)

            kmi = km.keymap_items.new(idname, key_type, value, shift=shift, ctrl=ctrl, alt=alt)

            if kmi:
                properties = item.get("properties")
                if properties:
                    for name, value in properties.items():
                        setattr(kmi.properties, name, value)
            addon_keymaps.append((km, kmi))


def unregister():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc: return

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()
