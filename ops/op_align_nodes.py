import bpy
from numpy import mean

# 节点偏移距离
C_DIS_X = 50
C_DIS_Y = 30


def connected_socket(self):
    """获取接口所链接的另一非reroute接口

    :param self: bpy.types.NodeSocket
    :return: list[bpy.types.NodeSocket] / None
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

    return _connected_sockets if len(_connected_sockets) != 0 else None


def get_dependence(node, selected_nodes=None):
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


def get_dependent(node, selected_nodes=None):
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


def dpifac():
    """获取用户屏幕缩放，用于矫正节点宽度/长度和摆放位置

    :return: Float
    """
    prefs = bpy.context.preferences.system
    return prefs.dpi * prefs.pixel_size / 72


def get_dimensions(node):
    """获取节点尺寸

    :param node: bpy.types.Node
    :return: (x,y) tuple
    """
    return node.dimensions.x / dpifac(), node.dimensions.y / dpifac()


def get_center_point(node):
    """获取节点中心点，用于评估尺寸和摆放位置

    :param node: bpy.types.Node
    :return: (x,y) tuple
    """
    dim_x, dim_y = get_dimensions(node)
    mid_x = (node.location.x - dim_x) / 2
    mid_y = (node.location.y - dim_y) / 2
    return mid_x, mid_y

### TODO 上下对齐（仅限3.2：快捷键新功能）
### TODO 制作动画

class MATHP_OT_align_dependence(bpy.types.Operator):
    bl_idname = 'mathp.align_dependence'
    bl_label = 'Align Dependence'

    aligned_nodes = []
    aligned_twice = []

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'active_node') and context.active_node

    def execute(self, context):
        self.aligned_nodes.clear()
        self.aligned_twice.clear()
        selected_nodes = context.selected_nodes
        print(selected_nodes)
        self.align_dependence(context.active_node, selected_nodes)

        return {'FINISHED'}

    def align_dependence(self, node, selected_nodes=None):
        dependence = get_dependence(node, selected_nodes)

        # 设置初始值
        dim_x, dim_y = get_dimensions(node)

        last_location_x = node.location.x
        last_dimensions_x = dim_x
        last_location_y = node.location.y
        last_dimensions_y = dim_y

        for i, sub_node in enumerate(dependence):
            # 跳过未选中节点
            if selected_nodes is not None:
                if sub_node not in selected_nodes: continue

            sub_dim_x, sub_dim_y = get_dimensions(sub_node)

            # 检查子节点是否已经被排列
            if sub_node in self.aligned_nodes:

                # 获取父依赖节点并取均值
                dependent_nodes = get_dependent(sub_node)

                sub_node.location.x = min(
                    [depend_node.location.x for depend_node in dependent_nodes]) - sub_dim_x - C_DIS_X
                sub_node.location.y = mean(
                    [get_center_point(depend_node)[1] for depend_node in dependent_nodes]) + sub_dim_y / 2
                self.aligned_twice.append(sub_node)  # not adjust anymore

            else:
                self.aligned_nodes.append(sub_node)
                # 对其第一个节点到依赖节点
                sub_node.location.x = last_location_x - sub_dim_x - C_DIS_X
                sub_node.location.y = last_location_y - last_dimensions_y - C_DIS_Y if i != 0 else last_location_y

                # 为下一个节点设置
                last_location_y = sub_node.location.y
                last_dimensions_y = sub_dim_y

            self.align_dependence(sub_node)

        return node


def register():
    bpy.utils.register_class(MATHP_OT_align_dependence)


def unregister():
    bpy.utils.unregister_class(MATHP_OT_align_dependence)
