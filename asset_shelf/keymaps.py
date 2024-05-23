# SPDX-FileCopyrightText: 2010-2023 Blender Foundation
#
# SPDX-License-Identifier: GPL-2.0-or-later

from typing import List, Tuple

import bpy

addon_keymaps: List[Tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]] = []


def register() -> None:
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon is None:
        # This happens when Blender is running in the background.
        return

    # Asset Shelf
    km = wm.keyconfigs.addon.keymaps.new(name="Asset Shelf")

    kmi = km.keymap_items.new("mathp.mat_double_click", "LEFTMOUSE", "DOUBLE_CLICK")
    addon_keymaps.append((km, kmi))
    # Drag to drop
    kmi = km.keymap_items.new("mathp.mat_drag_drop", "LEFTMOUSE", "CLICK_DRAG")
    addon_keymaps.append((km, kmi))
    # Press
    kmi = km.keymap_items.new("mathp.delete_asset", "X", "PRESS", ctrl=False, shift=False)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("mathp.asset_rename", "F2", "PRESS", ctrl=False, shift=False)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("mathp.asset_copy", "D", "PRESS", ctrl=False, shift=True)
    addon_keymaps.append((km, kmi))

    kmi = km.keymap_items.new("mathp.refresh_preview", "R", "PRESS", ctrl=False, alt=True)
    addon_keymaps.append((km, kmi))


def unregister() -> None:
    # Clear shortcuts from the keymap.
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
