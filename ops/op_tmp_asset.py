import bpy
import os

from bpy.types import Operator, Menu
from bpy.props import StringProperty, BoolProperty, EnumProperty
from pathlib import Path
from bpy_extras import asset_utils

from .op_edit_material_asset import get_local_selected_assets, tag_redraw
from .functions import ensure_current_file_asset_cats, C_TMP_ASSET_TAG, selectedAsset, _uuid
from bpy.utils import previews

G_MATERIAL_COUNT = 0  # 材质数量，用于更新临时资产
G_ACTIVE_MATS_LIST = []  # 选中材质列表


class MATHP_OT_set_tmp_asset(Operator):
    bl_idname = "mathp.set_tmp_asset"
    bl_label = "Set Temp Asset"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        for mat in bpy.data.materials:
            if mat.asset_data: continue
            if mat.is_grease_pencil: continue
            mat.asset_mark()
            mat.asset_generate_preview()
            mat.asset_data.tags.new(C_TMP_ASSET_TAG)

        tag_redraw()

        if bpy.data.filepath == '':
            return {'CANCELLED'}

        ensure_current_file_asset_cats()

        for mat in bpy.data.materials:
            if mat.asset_data is None: continue
            if C_TMP_ASSET_TAG in mat.asset_data.tags:
                if mat.asset_data.catalog_id != _uuid:
                    mat.asset_data.catalog_id = _uuid
        try:
            bpy.ops.asset.library_refresh()
        except Exception as e:
            print(e)

        return {'FINISHED'}


class MATHP_OT_clear_tmp_asset(Operator):
    bl_idname = 'mathp.clear_tmp_asset'
    bl_label = 'Clear Temp Asset'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        for mat in bpy.data.materials:
            if mat.asset_data is None: continue

            if C_TMP_ASSET_TAG in mat.asset_data.tags:
                mat.asset_clear()

        tag_redraw()

        return {'FINISHED'}


class MATHP_OT_set_true_asset(selectedAsset, Operator):
    """Apply Selected as True Assets"""
    bl_idname = 'mathp.set_true_asset'
    bl_label = 'Apply'

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            if C_TMP_ASSET_TAG in mat.asset_data.tags:
                tag = mat.asset_data.tags[C_TMP_ASSET_TAG]
                mat.asset_data.tags.remove(tag)
                self.report({'INFO'}, '{} is set as True Asset'.format(mat.name))

        tag_redraw()

        return {'FINISHED'}


class MATHP_OT_delete_asset(selectedAsset, Operator):
    """Delete Selected Materials"""
    bl_idname = 'mathp.delete_asset'
    bl_label = 'Delete'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            bpy.data.materials.remove(mat)

        bpy.ops.asset.library_refresh()

        return {'FINISHED'}


class MATHP_OT_duplicate_asset(selectedAsset, Operator):
    """Duplicate Active Item"""
    bl_idname = 'mathp.duplicate_asset'
    bl_label = 'Duplicate'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            mat.copy()

        for mat in selected_mats:
            context.space_data.activate_asset_by_id(mat)

        return {'FINISHED'}


class MATHP_OT_refresh_asset_pv(selectedAsset, Operator):
    bl_idname = 'mathp.refresh_asset_pv'
    bl_label = 'Refresh Preview'

    @classmethod
    def poll(cls, context):
        if hasattr(context, 'active_file'):
            return context.active_file and get_local_selected_assets(context)

    def execute(self, context):
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            mat.asset_generate_preview()

        return {'FINISHED'}


class MATHP_OT_rename_asset(selectedAsset, Operator):
    """Rename Active Item"""
    bl_idname = 'mathp.rename_asset'
    bl_label = 'Rename'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if hasattr(context, 'active_file'):
            return context.active_file and get_local_selected_assets(context)

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        active = get_local_selected_assets(context)[0]

        layout = self.layout
        layout.separator()
        layout.label(text='Name')
        if isinstance(active, bpy.types.Material):
            icon = 'MATERIAL'
        elif isinstance(active, bpy.types.Object):
            icon = 'OBJECT_DATA'
        elif isinstance(active, bpy.types.Collection):
            icon = 'GROUP'
        elif isinstance(active, bpy.types.World):
            icon = 'WORLD'
        else:
            icon = "ASSET_MANAGER"

        layout.prop(active, 'name', text='', icon=icon)
        layout.separator()

    def execute(self, context):
        return {'FINISHED'}


# icon注册
G_PV_COLL = {}
G_MAT_ICON_ID = {}  # name:id


def register_icon():
    # global G_PV_COLL, G_MAT_ICON_ID

    icon_dir = Path(__file__).parent.parent.joinpath('mat_lib')
    mats_icon = []

    for file in os.listdir(str(icon_dir)):
        if file.endswith('.png'):
            mats_icon.append(icon_dir.joinpath(file))
    # 注册
    pcoll = previews.new()

    for icon_path in mats_icon:
        pcoll.load(icon_path.name[:-4], str(icon_path), 'IMAGE')
        G_MAT_ICON_ID[icon_path.name[:-4]] = pcoll.get(icon_path.name[:-4]).icon_id

    G_PV_COLL['mathp_icon'] = pcoll


def unregister_icon():
    # global G_PV_COLL, G_MAT_ICON_ID

    for pcoll in G_PV_COLL.values():
        previews.remove(pcoll)
    G_PV_COLL.clear()

    G_MAT_ICON_ID.clear()


class MATHP_OT_select_material_obj(selectedAsset, Operator):
    bl_idname = 'mathp.select_material_obj'
    bl_label = 'Select Material Object'
    bl_options = {'UNDO'}

    def execute(self, context):
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]
        tmp_mesh = bpy.data.meshes.new('Temp')
        tmp_obj = bpy.data.objects.new('Temp',tmp_mesh)
        context.collection.objects.link(tmp_obj)
        bpy.context.view_layer.objects.active = tmp_obj

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        temp_obj = context.object
        for i, mat in enumerate(selected_mats):
            bpy.ops.object.material_slot_add()
            tmp_obj.material_slots[i].material = mat
        bpy.ops.object.select_linked(type='MATERIAL')
        bpy.data.objects.remove(temp_obj)
        return {'FINISHED'}


class MATHP_OT_add_material(Operator):
    """Add Material"""
    bl_idname = 'mathp.add_material'
    bl_label = 'Add Material'
    bl_options = {'REGISTER', 'UNDO'}

    dep_class = []  # 动态ops

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'selected_assets')

    def execute(self, context):
        # 清空动态注册op
        for cls in self.dep_class:
            bpy.utils.unregister_class(cls)
        self.dep_class.clear()

        # 获取材质库已有材质名
        icon_dir = Path(__file__).parent.parent.joinpath('mat_lib')
        blend_file = icon_dir.joinpath('mat.blend')
        with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
            mats = data_from.materials

        # 根据材质库材质动态注册
        def dy_modal(_self, _context, _event):
            if _event.type == 'TIMER':
                if _self.count < 10:
                    _self.count += 1
                else:
                    _context.area.spaces[0].activate_asset_by_id(_self.material)
                    _context.area.tag_redraw()

                    if _self._timer:
                        _context.window_manager.event_timer_remove(_self._timer)
                        _self._timer = None
                        return {'FINISHED'}

            return {'PASS_THROUGH'}

        def dy_invoke(_self, _context, _event):
            with bpy.data.libraries.load(_self.blend_file, link=False) as (data_from, data_to):
                data_to.materials = [_self.material]

            # 刷新资产库
            bpy.ops.asset.library_refresh()
            _self.material = data_to.materials[0]
            _self._timer = _context.window_manager.event_timer_add(0.01, window=_context.window)
            _context.window_manager.modal_handler_add(_self)
            return {"RUNNING_MODAL"}

        for i, mat in enumerate(mats):
            mat_name = mat
            op_cls = type("DynOp",
                          (bpy.types.Operator,),
                          {"bl_idname": f'wm.mathp_add_material_{i}',
                           "bl_label": mat_name,
                           "bl_description": 'Add',
                           # "execute": dy_execute,
                           'invoke': dy_invoke,
                           'modal': dy_modal,
                           # 自定义参数传入
                           'blend_file': str(blend_file),
                           'material': mat_name,
                           '_timer': None,
                           'count': 0
                           },
                          )
            self.dep_class.append(op_cls)

        for cls in self.dep_class:
            bpy.utils.register_class(cls)

        # 绘制动态菜单
        op = self

        def draw_custom_menu(self, context):
            global G_MAT_ICON_ID
            layout = self.layout
            layout.operator_context = 'INVOKE_DEFAULT'
            for i, cls in enumerate(op.dep_class):
                o = layout.operator(cls.bl_idname, icon_value=G_MAT_ICON_ID[cls.bl_label])

        # 弹出
        context.window_manager.popup_menu(draw_custom_menu, title='Material', icon='ADD')
        return {"FINISHED"}


class MATHP_MT_asset_browser_menu(Menu):
    bl_label = 'Material Helper'
    bl_idname = 'MATHP_MT_asset_browser_menu'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        layout.separator()
        layout.operator('mathp.clear_unused_material', icon='X')

        layout.separator()

        layout.operator('mathp.add_material', icon='ADD')
        layout.operator('mathp.duplicate_asset')
        layout.operator('mathp.rename_asset')
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator('mathp.replace_mat')
        layout.operator('mathp.delete_asset')
        layout.separator()

        layout.operator('mathp.set_true_asset', icon='ASSET_MANAGER')


def draw_asset_browser(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.menu('MATHP_MT_asset_browser_menu')
    row.separator()
    row.prop(context.scene, 'mathp_update_mat', toggle=True, icon='FILE_REFRESH')
    row.prop(context.window_manager, 'mathp_update_active_obj_mats', toggle=True, icon='UV_SYNC_SELECT')
    row.separator()
    row.operator(MATHP_OT_refresh_asset_pv.bl_idname, icon='FILE_REFRESH')
    row.operator(MATHP_OT_select_material_obj.bl_idname, icon='RESTRICT_SELECT_OFF')
    row.operator('mathp.edit_material_asset', icon='NODETREE')
    row.operator('mathp.replace_mat', icon='CON_TRANSLIKE')
    row.operator('mathp.clear_unused_material', icon='NODE_MATERIAL')


def draw_context_menu(self, context):
    if not hasattr(context, 'selected_assets'): return
    if len(context.selected_assets) == 0: return
    if not isinstance(context.selected_assets[0].local_id, bpy.types.Material): return

    layout = self.layout
    layout.operator('mathp.duplicate_asset')
    layout.operator('mathp.delete_asset')
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator('mathp.replace_mat')
    layout.separator()


from bpy.app.handlers import persistent


@persistent
def update_tmp_asset(scene, depsgraph):
    if scene.mathp_update_mat is False: return

    global G_MATERIAL_COUNT
    old_value = G_MATERIAL_COUNT

    if len(bpy.data.materials) != old_value:
        G_MATERIAL_COUNT = len(bpy.data.materials)
        bpy.ops.mathp.set_tmp_asset()


@persistent
def update_active_object_material(scene, depsgraph):
    wm = bpy.context.window_manager
    if scene.mathp_update_mat is False:
        return
    elif wm.mathp_update_active_obj_mats is False:
        return
    elif not hasattr(bpy.context, 'object'):
        return
    elif bpy.context.object is None:
        return
    elif bpy.context.object.type not in {'MESH', 'CURVE', 'FONT', 'META', 'VOLUME', 'GPENCIL', 'SURFACE'}:
        return
    elif len(bpy.context.object.material_slots) == 0:
        return
    # 获取面板
    asset_area = None
    for area in bpy.context.window.screen.areas:
        if area.type == 'FILE_BROWSER' and area.ui_type == 'ASSETS':
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


def update_user_control(self, context):
    if context.scene.mathp_update_mat is True:
        bpy.ops.mathp.set_tmp_asset()
    else:
        bpy.ops.mathp.clear_tmp_asset()


def remove_all_tmp_tags():
    for mat in bpy.data.materials:
        if mat.asset_data is None: continue
        for tag in mat.asset_data.tags:
            if tag.name == C_TMP_ASSET_TAG:
                mat.asset_data.tags.remove(tag)


classes = (
    MATHP_OT_set_tmp_asset,
    MATHP_OT_clear_tmp_asset,
    MATHP_OT_set_true_asset,
    MATHP_OT_delete_asset,
    MATHP_OT_duplicate_asset,
    MATHP_OT_rename_asset,
    MATHP_OT_add_material,
    MATHP_OT_refresh_asset_pv,
    MATHP_OT_select_material_obj,
)


def register_later(lock, t):
    # to prevent bug
    import time
    while not hasattr(bpy.context, 'scene'):
        time.sleep(5)
    wm = bpy.context.window_manager
    wm.mathp_update_active_obj_mats = True


def register():
    register_icon()

    for cls in classes:
        bpy.utils.register_class(cls)
    # 用户总控制开关
    bpy.types.Scene.mathp_update_mat = BoolProperty(name='Auto Update',
                                                    default=True,
                                                    description='If checked, the material will be automatically add as temp asset\nElse, temp assets will be cleared',
                                                    update=update_user_control)
    bpy.types.WindowManager.mathp_update_active_obj_mats = BoolProperty(name='Object / Material Select Sync',
                                                                        description="If checked, the active object's materials will be automatically selected",
                                                                        default=False)
    # handle
    bpy.app.handlers.depsgraph_update_post.append(update_tmp_asset)
    bpy.app.handlers.depsgraph_update_pre.append(update_active_object_material)
    # ui
    bpy.utils.register_class(MATHP_MT_asset_browser_menu)
    bpy.types.ASSETBROWSER_MT_editor_menus.append(draw_asset_browser)
    bpy.types.ASSETBROWSER_MT_context_menu.prepend(draw_context_menu)

    import threading
    lock = threading.Lock()
    lock_holder = threading.Thread(target=register_later, args=(lock, 5), name='Init_Scene2')
    lock_holder.daemon = True
    lock_holder.start()


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    remove_all_tmp_tags()
    unregister_icon()
    # handle
    bpy.app.handlers.depsgraph_update_post.remove(update_tmp_asset)
    bpy.app.handlers.depsgraph_update_pre.remove(update_active_object_material)
    del bpy.types.Scene.mathp_update_mat
    # ui
    bpy.utils.unregister_class(MATHP_MT_asset_browser_menu)
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(draw_asset_browser)
    bpy.types.ASSETBROWSER_MT_context_menu.remove(draw_context_menu)
