import bpy
import os

from bpy.types import Operator, Menu
from bpy.props import StringProperty, BoolProperty, EnumProperty
from pathlib import Path

from .op_edit_material_asset import get_local_selected_assets

from bpy.utils import previews

C_TMP_ASSET_TAG = 'tmp_asset_mathp'
G_MATERIAL_COUNT = 0  # 材质数量，用于更新临时资产


def tag_redraw():
    '''Redraw every region in Blender.'''
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            for region in area.regions:
                region.tag_redraw()


class selectedAsset:
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'selected_asset_files') and context.selected_asset_files


class MATHP_OT_set_tmp_asset(Operator):
    bl_idname = "mathp.set_tmp_asset"
    bl_label = "Set Temp Asset"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        for mat in bpy.data.materials:
            if mat.asset_data: continue

            mat.asset_mark()
            mat.asset_generate_preview()
            mat.asset_data.tags.new(C_TMP_ASSET_TAG)

        tag_redraw()

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
    bl_idname = 'mathp.set_true_asset'
    bl_label = 'Apply Selected as True Assets'

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


class MATHP_MT_delete_asset(selectedAsset, Operator):
    bl_idname = 'mathp.delete_asset'
    bl_label = 'Delete'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        match_obj = get_local_selected_assets(context)
        selected_mats = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

        for mat in selected_mats:
            mat.asset_clear()
            bpy.data.materials.remove(mat)

        return {'FINISHED'}


class MATHP_OT_add_material(Operator):
    bl_idname = 'mathp.add_material'
    bl_label = 'Add Material'
    bl_options = {'REGISTER', 'UNDO'}

    dep_class = []  # 动态ops
    preview_collections = {}  # 动态icon

    def invoke(self, context, event):
        # 清空icon预览
        for pcoll in self.preview_collections.values():
            previews.remove(pcoll)
        self.preview_collections.clear()
        # 清空动态注册op
        for cls in self.dep_class:
            bpy.utils.unregister_class(cls)
        self.dep_class.clear()

        # 获取材质库已有材质名
        icon_dir = Path(__file__).parent.parent.joinpath('mat_lib')
        blend_file = icon_dir.joinpath('mat.blend')
        with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
            mats = data_from.materials
        # 寻找icon
        mats_icon = []
        mats_icon_id = []

        for file in os.listdir(str(icon_dir)):
            if file.endswith('.png') and file[:-4] in mats:
                mats_icon.append(icon_dir.joinpath(file))
        # 注册
        for icon_path in mats_icon:
            pcoll = previews.new()
            pcoll.load(icon_path.name[:-4], str(icon_path), 'IMAGE')
            self.preview_collections['mathp_icon'] = pcoll
            mats_icon_id.append(pcoll.get(icon_path.name[:-4]).icon_id)

            # 根据材质库材质动态注册

        def dy_execute(self, context):
            # 导入
            with bpy.data.libraries.load(self.blend_file, link=False) as (data_from, data_to):
                data_to.materials = [self.material]
            # 刷新资产库
            bpy.ops.asset.library_refresh()

            return {'FINISHED'}

        for i, icon_path in enumerate(mats_icon):
            mat_name = icon_path.name[:-4]
            op_cls = type("DynOp",
                          (bpy.types.Operator,),
                          {"bl_idname": f'wm.mathp_add_material_{i}',
                           "bl_label": mat_name,
                           "bl_description": 'Add',
                           "execute": dy_execute,
                           # 自定义参数传入
                           'blend_file': str(blend_file),
                           'material': mat_name,
                           },
                          )
            self.dep_class.append(op_cls)

        for cls in self.dep_class:
            bpy.utils.register_class(cls)

        # 绘制动态菜单
        op = self

        def draw_custom_menu(self, context):
            layout = self.layout
            for i, cls in enumerate(op.dep_class):
                layout.operator(cls.bl_idname, icon_value=mats_icon_id[i])

        # 弹出
        context.window_manager.popup_menu(draw_custom_menu, title='Material', icon='ADD')
        return {'FINISHED'}


class MATHP_MT_asset_browser_menu(Menu):
    bl_label = 'Material Helper'
    bl_idname = 'MATHP_MT_asset_browser_menu'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        layout.prop(context.scene, 'mathp_update_mat')
        layout.separator()
        layout.operator('mathp.add_material', icon='ADD')
        layout.operator('mathp.set_true_asset', icon='ASSET_MANAGER')


def draw_asset_browser(self, context):
    layout = self.layout
    layout.menu('MATHP_MT_asset_browser_menu')


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
def update_load_file_post(scene):
    if bpy.context.scene.mathp_update_mat is True:
        bpy.ops.mathp.set_tmp_asset()
    else:
        bpy.ops.mathp.clear_tmp_asset()


def update_user_control(self, context):
    if context.scene.mathp_update_mat is True:
        bpy.ops.mathp.set_tmp_asset()
    else:
        bpy.ops.mathp.clear_tmp_asset()


def register():
    bpy.utils.register_class(MATHP_OT_set_tmp_asset)
    bpy.utils.register_class(MATHP_OT_clear_tmp_asset)
    bpy.utils.register_class(MATHP_OT_set_true_asset)
    bpy.utils.register_class(MATHP_MT_delete_asset)
    bpy.utils.register_class(MATHP_OT_add_material)
    # 用户总控制开关
    bpy.types.Scene.mathp_update_mat = BoolProperty(name='Auto Update',
                                                    default=True,
                                                    description='If checked, the material will be automatically add as temp asset\nElse, temp assets will be cleared',
                                                    update=update_user_control)
    # handle
    bpy.app.handlers.depsgraph_update_post.append(update_tmp_asset)
    bpy.app.handlers.load_post.append(update_load_file_post)
    # ui
    bpy.utils.register_class(MATHP_MT_asset_browser_menu)
    bpy.types.ASSETBROWSER_MT_editor_menus.append(draw_asset_browser)


def unregister():
    bpy.utils.unregister_class(MATHP_OT_set_tmp_asset)
    bpy.utils.unregister_class(MATHP_OT_clear_tmp_asset)
    bpy.utils.unregister_class(MATHP_OT_set_true_asset)
    bpy.utils.unregister_class(MATHP_MT_delete_asset)
    bpy.utils.unregister_class(MATHP_OT_add_material)
    # handle
    bpy.app.handlers.depsgraph_update_post.remove(update_tmp_asset)
    bpy.app.handlers.load_post.remove(update_load_file_post)
    del bpy.types.Scene.mathp_update_mat
    # ui
    bpy.utils.unregister_class(MATHP_MT_asset_browser_menu)
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(draw_asset_browser)
