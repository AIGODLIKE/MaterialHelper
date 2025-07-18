
def update_active_object_material(scene, depsgraph):
    wm = bpy.context.window_manager
    if scene.mathp_update_mat is False:
        return
    elif wm.mathp_update_active_obj_mats is False:
        return
    elif not hasattr(bpy.context, "object"):
        return
    elif bpy.context.object is None:
        return
    elif bpy.context.object.type not in {"MESH", "CURVE", "FONT", "META", "VOLUME", "GPENCIL", "SURFACE"}:
        return
    elif len(bpy.context.object.material_slots) == 0:
        return
    # 获取面板
    asset_area = None
    for area in bpy.context.window.screen.areas:
        if area.type == "FILE_BROWSER" and area.ui_type == "ASSETS":
            asset_area = area
            break

    if asset_area is None: return

    # 获取材质
    global G_ACTIVE_MATS_LIST
    G_ACTIVE_MATS_LIST.clear()

    for mat_slot in bpy.context.object.material_slots:
        G_ACTIVE_MATS_LIST.append(mat_slot.material)

    G_ACTIVE_MATS_LIST.reverse()

    try:
        asset_area.spaces[0].deselect_all()  # window上有bug
        # 激活材质
        space_data = asset_area.spaces[0]
        assert asset_utils.SpaceAssetInfo.is_asset_browser(space_data)

        if bpy.context.object.select_get():
            for mat in G_ACTIVE_MATS_LIST:
                space_data.activate_asset_by_id(mat, deferred=False)


    except Exception as e:
        print(e)