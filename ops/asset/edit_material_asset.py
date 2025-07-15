from contextlib import contextmanager
from pathlib import Path
from typing import Union

import bpy

from ...utils import get_pref

def allowSaveUpdate():
    return bpy.context.window_manager.mathp_global_update is False


@contextmanager
def SaveUpdate():
    bpy.context.window_manager.mathp_global_update = True
    yield
    bpy.context.window_manager.mathp_global_update = False




class MATHP_OT_edit_material_asset(bpy.types.Operator):
    bl_idname = 'mathp.edit_material_asset'
    bl_label = 'Edit Material Asset'

    material: bpy.props.StringProperty(name='Material Name', options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return (hasattr(context, 'selected_assets') and context.selected_assets) or context.asset

    def _return(self, msg, type='INFO'):
        """
        :param msg: 报告给用户的信息
        :param type: 信息/警告/错误弹窗
        :return: {'CANCELLED'}/{'FINISHED'}
        """

        self.report({type}, msg)
        if type == 'INFO':
            return {"FINISHED"}
        else:
            return {"CANCELLED"}

    def get_data(self, data_lib, name):
        """

        :param data_lib: 数据类型 str
        :param name: 数据名字
        :return:
        """
        data_lib = getattr(bpy.data, data_lib)
        data = data_lib.get(name)
        if not data:
            data_lib.new(name=name)

        return data

    def execute(self, context):
        if self.material:
            selected_mat = [bpy.data.materials[self.material], ]
        else:
            match_obj = get_local_selected_assets(context)
            selected_mat = [obj for obj in match_obj if isinstance(obj, bpy.types.Material)]

            if not selected_mat:
                return self._return(msg='请选择一个本地材质资产', type='WARNING')
            # print(selected_mat)

        # 创建集合
        tmp_coll = bpy.data.collections[
            'tmp_mathp'] if 'tmp_mathp' in bpy.data.collections else bpy.data.collections.new(
            'tmp_mathp')
        if 'tmp_mathp' not in context.scene.collection.children:
            context.scene.collection.children.link(tmp_coll)

        # 设置材质球/材质

        set_shader_ball_mat(selected_mat[0], tmp_coll)
        selected_mat[0].asset_generate_preview()

        # 设置鼠标位置，以便弹窗出现在正中央
        w = context.window
        w_center_x, w_center_y = w.width / 2, w.height / 2
        w.cursor_warp(int(w_center_x), int(w_center_y))
        # 弹窗
        pop_up_window(style=get_pref().window_style)

        return {'FINISHED'}


from bpy.app.handlers import persistent


@persistent
def del_tmp_obj(scene, depsgraph):
    """删除用于预览的模型/网格/屏幕缓存

    :param scene:
    :param depsgraph:
    :return:
    """
    return
    try:
        _ = bpy.context.window_manager.windows[State.window_count - 1]
        return
    except IndexError:
        pass
    finally:
        update_window_count()

    if allowSaveUpdate():
        if mat := bpy.data.materials.get(State.last_edit_mat, default=False):
            mat.asset_generate_preview()

        coll = bpy.data.collections.get('tmp_mathp')
        if coll:
            # 清理临时物体
            for obj in bpy.data.collections['tmp_mathp'].objects:
                me = obj.data
                bpy.data.objects.remove(obj)
                bpy.data.meshes.remove(me)

            bpy.data.collections.remove(coll)

        if 'tmp_mathp' in bpy.data.screens:
            # 清理多余screen
            for s in bpy.data.screens:
                if not s.name.startswith('tmp_mathp'):
                    continue
                s.user_clear()


def update_shader_ball(self, context):
    coll = bpy.data.collections.get('tmp_mathp')

    if not coll: return

    mat = self.id_data

    for obj in bpy.data.collections['tmp_mathp'].objects:
        me = obj.data
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(me)

    set_shader_ball_mat(mat, coll)
    mat.asset_generate_preview()

    for a in context.window.screen.areas:
        if a.type == 'VIEW_3D':
            a.spaces[0].lock_object = bpy.context.object


def register():
    bpy.utils.register_class(MATHP_OT_edit_material_asset)
    bpy.utils.register_class(MATHP_OT_update_mat_pv)
    bpy.app.handlers.depsgraph_update_pre.append(del_tmp_obj)


def unregister():
    bpy.app.handlers.depsgraph_update_pre.remove(del_tmp_obj)
    bpy.utils.unregister_class(MATHP_OT_edit_material_asset)
    bpy.utils.unregister_class(MATHP_OT_update_mat_pv)
