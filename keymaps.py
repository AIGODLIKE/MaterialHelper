import bpy

addon_keymaps = []

keymaps = []
from mathutils import Vector, Euler, Matrix


def get_kmi_operator_properties(kmi: 'bpy.types.KeyMapItem') -> dict:
    """获取kmi操作符的属性
    """
    properties = kmi.properties
    prop_keys = dict(properties.items()).keys()
    dictionary = {i: getattr(properties, i, None) for i in prop_keys}
    del_key = []
    for item in dictionary:
        prop = getattr(properties, item, None)
        typ = type(prop)
        if prop:
            if typ == Vector:
                # 属性阵列-浮点数组
                dictionary[item] = dictionary[item].to_tuple()
            elif typ == Euler:
                dictionary[item] = dictionary[item][:]
            elif typ == Matrix:
                dictionary[item] = tuple(i[:] for i in dictionary[item])
            elif typ == bpy.types.bpy_prop_array:
                dictionary[item] = dictionary[item][:]
            elif typ in (str, bool, float, int, set, list, tuple):
                ...
            elif typ.__name__ in [
                'TRANSFORM_OT_shrink_fatten',
                'TRANSFORM_OT_translate',
                'TRANSFORM_OT_edge_slide',
                'NLA_OT_duplicate',
                'ACTION_OT_duplicate',
                'GRAPH_OT_duplicate',
                'TRANSFORM_OT_translate',
                'OBJECT_OT_duplicate',
                'MESH_OT_loopcut',
                'MESH_OT_rip_edge',
                'MESH_OT_rip',
                'MESH_OT_duplicate',
                'MESH_OT_offset_edge_loops',
                'MESH_OT_extrude_faces_indiv',
            ]:  # 一些奇怪的操作符属性,不太好解析也用不上
                ...
                del_key.append(item)
            else:
                print('emm 未知属性,', typ, dictionary[item])
                del_key.append(item)
    for i in del_key:
        dictionary.pop(i)
    return dictionary


def draw_keymap(layout):
    from rna_keymap_ui import draw_kmi

    kc = bpy.context.window_manager.keyconfigs.user
    for km, kmi in keymaps:
        km = kc.keymaps.get(km.name)
        if km:
            kmi = km.keymap_items.get(kmi.idname, get_kmi_operator_properties(kmi))
            if kmi:
                keymap = None
                if (not kmi.is_user_defined) and kmi.is_user_modified:
                    keymap = km
                layout.context_pointer_set("keymap", keymap)

                draw_kmi(["USER", "ADDON", "DEFAULT"], kc, km, kmi, layout, 0)



KEYMAPS = {
    "File Browser": [
        {"idname": "mathp.edit_material_asset", "type": "LEFTMOUSE", "value": "DOUBLE_CLICK"},
        {"idname": "mathp.delete_asset", "type": "X", "value": "PRESS"},
        {"idname": "mathp.apply_asset", "type": "A", "value": "PRESS", "ctrl": True},
        {"idname": "mathp.duplicate_asset", "type": "D", "value": "PRESS", "shift": True},
        {"idname": "mathp.rename_asset", "type": "F2", "value": "PRESS"},
        {"idname": "wm.call_menu", "type": "A", "value": "PRESS", "shift": True,
         "properties": {"name": "MATERIAL_HELPER_MT_add_material_menu"}},
    ],
    "Node Editor": [
        {"idname": "mathp.align_dependence", "type": "A", "value": "PRESS", "ctrl": True},
        {"idname": "mathp.move_dependence", "type": "D", "value": "PRESS"}
    ],
    "3D View Generic": [
        {"idname": "mathp.material_picker", "type": "BUTTON4MOUSE",
         "value": "PRESS", "alt": True},
        {"idname": "mathp.material_drag", "type": "LEFTMOUSE",
         "value": "CLICK_DRAG", "alt": True, "ctrl": True, "shift": True},
        {"idname": "mathp.material_assign_by_modal", "type": "BUTTON4MOUSE",
         "value": "PRESS", "alt": True, "ctrl": True, "shift": True}
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
