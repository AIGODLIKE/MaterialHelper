import bpy

addon_keymaps = []


def register():
    wm = bpy.context.window_manager
    if not wm.keyconfigs.addon: return
    # 双击点开材质
    km = wm.keyconfigs.addon.keymaps.new(name='File Browser', space_type='FILE_BROWSER')
    kmi = km.keymap_items.new("mathp.edit_material_asset", 'LEFTMOUSE', 'DOUBLE_CLICK', ctrl=False, shift=False)
    addon_keymaps.append((km, kmi))
    # 删除材质
    km = wm.keyconfigs.addon.keymaps.new(name='File Browser', space_type='FILE_BROWSER')
    kmi = km.keymap_items.new("mathp.delete_asset", 'X', 'PRESS', ctrl=False, shift=False)
    addon_keymaps.append((km, kmi))
    # 应用资产
    km = wm.keyconfigs.addon.keymaps.new(name='File Browser', space_type='FILE_BROWSER')
    kmi = km.keymap_items.new("mathp.set_true_asset", 'A', 'PRESS', ctrl=True, shift=False)
    addon_keymaps.append((km, kmi))
    # 复制资产
    km = wm.keyconfigs.addon.keymaps.new(name='File Browser', space_type='FILE_BROWSER')
    kmi = km.keymap_items.new("mathp.duplicate_asset", 'D', 'PRESS', ctrl=False, shift=True)
    addon_keymaps.append((km, kmi))
    # 添加资产
    km = wm.keyconfigs.addon.keymaps.new(name='File Browser', space_type='FILE_BROWSER')
    kmi = km.keymap_items.new("mathp.add_material", 'A', 'PRESS', ctrl=False, shift=True)
    addon_keymaps.append((km, kmi))
    # 节点对齐
    km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
    kmi = km.keymap_items.new('mathp.align_dependence', 'A', 'PRESS', ctrl=True)
    addon_keymaps.append((km, kmi))
    # 控制依赖项
    km = wm.keyconfigs.addon.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
    kmi = km.keymap_items.new('mathp.move_dependence', 'D', 'PRESS')
    addon_keymaps.append((km, kmi))


def unregister():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc: return

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

    addon_keymaps.clear()
