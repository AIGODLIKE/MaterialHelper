from math import sqrt
from typing import Optional

import blf
import bpy
from numpy import mean

from ..utils import get_pref


# 节点偏移距离
def dis_x() -> int:
    return get_pref().node_dis_x


def dis_y() -> int:
    return get_pref().node_dis_y


def connected_socket(self) -> list[bpy.types.NodeSocket]:
    """获取接口所链接的另一非reroute接口

    :param self: bpy.types.NodeSocket
    :return: list[bpy.types.NodeSocket]
    """
    _connected_sockets = []

    socket = self
    if socket.is_output:
        # while socket.is_linked and socket.links[0].to_node.bl_rna.name == 'Reroute':
        #     socket = socket.links[0].to_node.outputs[0]
        if socket.is_linked:
            for link in socket.links:
                _connected_sockets.append(link.to_socket)
    else:
        # while socket.is_linked and socket.links[0].from_node.bl_rna.name == 'Reroute':
        #     socket = socket.links[0].from_node.inputs[0]
        if socket.is_linked:
            for link in socket.links:
                _connected_sockets.append(link.from_socket)

    return _connected_sockets


def get_dependence(node, selected_nodes=None) -> list[bpy.types.Node]:
    """获取节点子依赖项

    :param node:  bpy.types.Node
    :param selected_nodes:  list[bpy.types.Node]
    :return: list[bpy.types.Node]
    """
    dependence_nodes = list()
    for input in node.inputs:
        _connected_sockets = connected_socket(input)
        if not _connected_sockets: continue

        for socket in _connected_sockets:
            if (selected_nodes and socket.node in selected_nodes) or (selected_nodes is None):
                dependence_nodes.append(socket.node)

    return dependence_nodes


def get_dependent(node: bpy.types.Node, selected_nodes: Optional[list[bpy.types.Node]] = None) -> list[bpy.types.Node]:
    """获取节点父依赖项

    :param node:  bpy.types.Node
    :param selected_nodes:  list[bpy.types.Node]
    :return: list[bpy.types.Node]
    """
    dependent_nodes = list()
    for output in node.outputs:
        _connected_sockets = connected_socket(output)

        if not _connected_sockets: continue

        for socket in _connected_sockets:
            if (selected_nodes and socket.node in selected_nodes) or (selected_nodes is None):
                dependent_nodes.append(socket.node)

    return dependent_nodes


def get_all_dependence(node: bpy.types.Node, selected_nodes: Optional[list[bpy.types.Node]] = None):
    """获取节点所有依赖项

    :param node:  bpy.types.Node
    :param selected_nodes:  list[bpy.types.Node]
    :return: list[bpy.types.Node]
    """
    all_dependence_nodes = list()
    dependence = get_dependence(node, selected_nodes)

    for dependence_node in dependence:
        all_dependence_nodes.append(dependence_node)

        sub_dependence = get_all_dependence(dependence_node, selected_nodes)
        for sub_node in sub_dependence:
            if sub_node not in all_dependence_nodes:
                all_dependence_nodes.append(sub_node)

    return all_dependence_nodes


def get_all_dependent(node: bpy.types.Node, selected_nodes: Optional[list[bpy.types.Node]] = None):
    """获取节点所有父级依赖项

    :param node:  bpy.types.Node
    :param selected_nodes:  list[bpy.types.Node]
    :return: list[bpy.types.Node]
    """
    all_dependent_nodes = list()
    dependent = get_dependent(node, selected_nodes)

    for dependent_node in dependent:
        all_dependent_nodes.append(dependent_node)

        sub_dependent = get_all_dependent(dependent_node, selected_nodes)
        for sub_node in sub_dependent:
            if sub_node not in all_dependent_nodes:
                all_dependent_nodes.append(sub_node)

    return all_dependent_nodes


def dpifac() -> float:
    """获取用户屏幕缩放，用于矫正节点宽度/长度和摆放位置

    :return: Float
    """
    prefs = bpy.context.preferences.system
    return prefs.dpi * prefs.pixel_size / 72


def get_dimensions(node) -> tuple[float, float]:
    """获取节点尺寸

    :param node: bpy.types.Node
    :return: (x,y) tuple
    """
    return node.dimensions.x / dpifac(), node.dimensions.y / dpifac()


def get_center_point(node, loc) -> tuple[float, float]:
    """获取节点中心点，用于评估尺寸和摆放位置

    :param node: bpy.types.Node
    :param loc: (x,y)
    :return: (x,y) tuple
    """

    dim_x, dim_y = get_dimensions(node)
    mid_x = (loc[0] - dim_x) / 2
    mid_y = (loc[1] - dim_y) / 2
    return mid_x, mid_y


def get_offset_from_anim(fac) -> float:
    """从动画值获取偏移比例

    :param fac: 动画完成比，0~1
    :return: 偏移比
    """

    return sqrt(min(max(fac, 0), 1))


def deselect_node(context):
    for node in context.space_data.edit_tree.nodes:
        node.select = False


mathp_node_move = False


class MATHP_OT_move_dependence(bpy.types.Operator):
    bl_idname = 'mathp.move_dependence'
    bl_label = 'Move Dependence'
    bl_options = {'GRAB_CURSOR', 'BLOCKING'}

    # 传递
    target_node = None  # 一开始鼠标所在节点
    # 初始值
    ori_mouse_x = None  # 用于检测鼠标位移是否超过阈值
    ori_mouse_y = None
    threshold_x = 50  # 用于检测命令指向

    ori_selected_nodes = None  # 用于撤销操作
    ori_node_loc_dict = None  # 用于撤销操作

    # 储存
    dependent = []
    dependence = []
    # 绘制
    _handle = None

    @classmethod
    def poll(cls, context):
        global mathp_node_move
        if mathp_node_move:
            return False
        return hasattr(context, 'selected_nodes')

    def remove_handler(self, context):
        global mathp_node_move
        mathp_node_move = False
        context.window.cursor_modal_restore()

    def append_handler(self, context):
        global mathp_node_move
        mathp_node_move = True
        context.window.cursor_modal_set('SCROLL_X')
        # 添加
        context.window_manager.modal_handler_add(self)

    def invoke(self, context, event):
        from ..utils.node_wrangler import node_at_pos
        # 初始化
        self.dependence.clear()
        self.dependent.clear()
        self.ori_selected_nodes = context.selected_nodes.copy()
        self.ori_node_loc_dict = {node: tuple(node.location) for node in self.ori_selected_nodes}
        # 储存初始鼠标位置
        self.mouse_pos = [0, 0]
        self.ori_mouse_x = event.mouse_x
        self.ori_mouse_y = event.mouse_y
        self.mouseDX = event.mouse_x
        self.mouseDY = event.mouse_y
        # 获取对应节点
        self.target_node = node_at_pos(context.space_data.edit_tree.nodes, context, event)
        self.dependence = get_all_dependence(self.target_node)
        self.dependent = get_all_dependent(self.target_node)

        self.append_handler(context)

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        # 重绘制，用于更新节点尺寸
        context.area.tag_redraw()
        self.mouse_pos = event.mouse_region_x, event.mouse_region_y

        # 移动子级
        if event.type == 'MOUSEMOVE':
            if event.mouse_x - self.ori_mouse_x < self.threshold_x:
                deselect_node(context)

                for node in self.dependence:
                    node.select = True

            # 选择父级
            elif event.mouse_x - self.ori_mouse_x > self.threshold_x:
                deselect_node(context)

                for node in self.dependent:
                    node.select = True


        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            # 还原
            deselect_node(context)

            for node in self.ori_selected_nodes:
                node.select = True

            for node in self.ori_node_loc_dict:
                node.location = self.ori_node_loc_dict[node]

            self.remove_handler(context)
            return {'CANCELLED'}

        elif event.type == 'LEFTMOUSE':
            self.remove_handler(context)
            bpy.ops.transform.translate('INVOKE_DEFAULT')
            return {'FINISHED'}

        return {'RUNNING_MODAL'}


def draw_process_callback_px(self, context):
    font_id = 0
    step = 8

    # blf.size(font_id, 8, 120)
    blf.position(font_id, self.draw_pos[0], self.draw_pos[1] + step, 0)
    blf.color(font_id, 1, 1, 1, 0.5)
    blf.draw(font_id, f"对齐中..{min(int(self.anim_fac / 2 * 100), 100)} %")


### TODO 单个节点到多个父级，父级间有依赖关系时候该节点过低的
mathp_node_anim = False


class MATHP_OT_align_dependence(bpy.types.Operator):
    bl_idname = 'mathp.align_dependence'
    bl_label = 'Align Dependence Nodes'

    node_loc_dict = None  # node:{ori_loc:(x,y),tg_loc:(x,y)}

    target_node = None
    # 动画控制
    anim_fac = 0  # 动画比例 0~1
    anim_iter = 30  # 动画更新 秒
    anim_time = 0.05  # 持续时间 秒
    # handle
    _timer = None
    _handle = None
    # ui
    draw_pos = None

    @classmethod
    def poll(cls, context):
        if not mathp_node_anim:
            return hasattr(context, 'selected_nodes') and len(context.selected_nodes) != 0
        return False

    def append_handle(self):
        global mathp_node_anim
        self._timer = bpy.context.window_manager.event_timer_add(self.anim_time / self.anim_iter,
                                                                 window=bpy.context.window)  # 添加计时器检测状态
        args = (self, bpy.context)
        self._handle = bpy.types.SpaceNodeEditor.draw_handler_add(draw_process_callback_px, args, 'WINDOW',
                                                                  'POST_PIXEL')
        bpy.context.window_manager.modal_handler_add(self)
        mathp_node_anim = True

    def remove_handle(self):
        global mathp_node_anim
        bpy.types.SpaceNodeEditor.draw_handler_remove(self._handle, 'WINDOW')
        bpy.context.window_manager.event_timer_remove(self._timer)
        mathp_node_anim = False

    def invoke(self, context, event):
        from ..utils.node_wrangler import node_at_pos
        # 初始化
        self.node_loc_dict = dict()
        self._timer = None
        self.anim_fac = 0
        self.draw_pos = [0, 0]
        # 获取鼠标下的节点
        self.target_node = node_at_pos(context.space_data.edit_tree.nodes, context, event)
        selected_nodes = tuple(list(context.selected_nodes) + [self.target_node])
        # 获取位置
        self.align_dependence(self.target_node, selected_nodes, check_dependent=True)

        self.append_handle()
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        from ..utils.node_wrangler import abs_node_location
        if event.type == 'TIMER':
            # 绘制
            # --------
            node = self.target_node
            loc_x = (abs_node_location(node)[0] + 1) * dpifac()
            loc_y = (abs_node_location(node)[1] + 1) * dpifac()

            dim_x = node.dimensions.x
            dim_y = node.dimensions.y

            top_left = (loc_x, loc_y + dim_y / 2) if node.hide else (loc_x, loc_y)
            # 获取视窗位置
            self.draw_pos = bpy.context.region.view2d.view_to_region(top_left[0], top_left[1], clip=False)
            # --------

            if self.anim_fac >= 1 + 1:  # 添加1动画延迟以完成动画
                self.remove_handle()
                # 强制对齐
                for node, loc_info in self.node_loc_dict.items():
                    node.location = loc_info['tg_loc']

                return {'FINISHED'}
            # 对节点依次进行移动动画
            for i, node in enumerate(self.node_loc_dict.keys()):
                delay = i / len(self.node_loc_dict)
                self.offset_node(node, self.anim_fac, delay)

            self.anim_fac += 1 / (self.anim_iter + 1)  # last delay

        return {"PASS_THROUGH"}

    def offset_node(self, node, anim_fac, delay=0.1):
        """

        :param node: bpy.types.Node
        :param anim_fac: 动画比 0~1
        :param delay: 延迟
        :return:
        """
        ori_loc = self.node_loc_dict[node]['ori_loc']
        tg_loc = self.node_loc_dict[node]['tg_loc']

        offset_fac = get_offset_from_anim(anim_fac - delay)

        offset_x = (tg_loc[0] - ori_loc[0]) * offset_fac
        offset_y = (tg_loc[1] - ori_loc[1]) * offset_fac

        node.location = ori_loc[0] + offset_x, ori_loc[1] + offset_y

    def align_dependence(self, node, selected_nodes=None, check_dependent=False):
        """提取节点的目标位置，用于动画

        :param node: bpy.types.Node
        :param selected_nodes: list[bpy.types.Node]
        :parm check_dependent: 检查父级依赖
        :return: bpy.types.Node
        """

        dependence = get_dependence(node, selected_nodes)

        # 设置初始值
        dim_x, dim_y = get_dimensions(node)

        if node in self.node_loc_dict:
            last_location_x, last_location_y = self.node_loc_dict[node]['tg_loc']
        else:
            last_location_x = node.location.x
            last_location_y = node.location.y
            # active node as dependent
            self.node_loc_dict[node] = {'ori_loc': tuple(node.location),
                                        'tg_loc': tuple(node.location)}

        last_dimensions_x = dim_x
        last_dimensions_y = dim_y

        for i, sub_node in enumerate(dependence):
            # 跳过未选中节点
            if selected_nodes and sub_node not in selected_nodes: continue

            sub_dim_x, sub_dim_y = get_dimensions(sub_node)

            # 对齐父级依赖
            if check_dependent:
                dependent_nodes = get_dependent(sub_node, selected_nodes)
                if len(dependent_nodes) > 1:
                    ori_loc = (sub_node.location.x, sub_node.location.y)

                    dep_loc_x = list()
                    dep_loc_y = list()

                    for i, depend_node in enumerate(dependent_nodes):
                        if depend_node in self.node_loc_dict:
                            dep_loc_x.append(self.node_loc_dict[depend_node]['tg_loc'][0])
                            dep_loc_y.append(self.node_loc_dict[depend_node]['tg_loc'][1])

                        else:
                            dep_loc_x.append(depend_node.location.x)
                            dep_loc_y.append(depend_node.location.y)

                    tg_loc_x = min(dep_loc_x) - sub_dim_x - dis_x()
                    tg_loc_y = mean(dep_loc_y)

                    # 记录位置用于动画
                    self.node_loc_dict[sub_node] = {'ori_loc': ori_loc,
                                                    'tg_loc': (tg_loc_x, tg_loc_y)}

                elif len(dependent_nodes) == 1:
                    # 排列同层级自己
                    parent_node = dependent_nodes[0]
                    self.align_dependence(parent_node, selected_nodes)


            # 忽略父级依赖
            else:
                ori_loc = (sub_node.location.x, sub_node.location.y)
                # 目标位置 = 上一个节点位置-当前节点宽度-间隔，y轴向对其第一个节点到依赖节点
                tg_loc_x = last_location_x - sub_dim_x - dis_x()
                tg_loc_y = last_location_y - last_dimensions_y - dis_y() if i != 0 else last_location_y
                # 记录位置用于动画
                self.node_loc_dict[sub_node] = {'ori_loc': ori_loc,
                                                'tg_loc': (tg_loc_x, tg_loc_y)}
                # 为下一个节点设置
                last_location_y = tg_loc_y
                last_dimensions_y = sub_dim_y

            self.align_dependence(sub_node, selected_nodes, check_dependent)

        return node
