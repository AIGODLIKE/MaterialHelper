from math import hypot

import bpy

def dpifac() -> float:
    """获取用户屏幕缩放，用于矫正节点宽度/长度和摆放位置

    :return: Float
    """
    prefs = bpy.context.preferences.system
    return prefs.dpi * prefs.pixel_size / 72


# 以下三个函数来自node wrangler
# 用于替换原来操作逻辑：选中项对齐激活项 -> 选中项对齐鼠标所在位置项

def abs_node_location(node) -> tuple[float, float]:
    if node.parent is None:
        return node.location

    return node.location + abs_node_location(node.parent)


def store_mouse_cursor(context, event) -> None:
    space = context.space_data
    tree = space.edit_tree

    # convert mouse position to the View2D for later node placement
    if context.region.type == 'WINDOW':
        space.cursor_location_from_region(event.mouse_region_x, event.mouse_region_y)
    else:
        space.cursor_location = tree.view_center


def node_at_pos(nodes, context, event) -> bpy.types.Node:
    nodes_under_mouse = []
    target_node = None

    store_mouse_cursor(context, event)
    x, y = context.space_data.cursor_location

    # Make a list of each corner (and middle of border) for each node.
    # Will be sorted to find nearest point and thus nearest node
    node_points_with_dist = []
    for node in nodes:
        skipnode = False
        if node.type == 'FRAME': continue  # no point trying to link to a frame node

        dimx = node.dimensions.x / dpifac()
        dimy = node.dimensions.y / dpifac()
        locx, locy = abs_node_location(node)

        if skipnode: continue

        node_points_with_dist.append([node, hypot(x - locx, y - locy)])  # Top Left
        node_points_with_dist.append([node, hypot(x - (locx + dimx), y - locy)])  # Top Right
        node_points_with_dist.append([node, hypot(x - locx, y - (locy - dimy))])  # Bottom Left
        node_points_with_dist.append([node, hypot(x - (locx + dimx), y - (locy - dimy))])  # Bottom Right

        node_points_with_dist.append([node, hypot(x - (locx + (dimx / 2)), y - locy)])  # Mid Top
        node_points_with_dist.append([node, hypot(x - (locx + (dimx / 2)), y - (locy - dimy))])  # Mid Bottom
        node_points_with_dist.append([node, hypot(x - locx, y - (locy - (dimy / 2)))])  # Mid Left
        node_points_with_dist.append([node, hypot(x - (locx + dimx), y - (locy - (dimy / 2)))])  # Mid Right

    nearest_node = sorted(node_points_with_dist, key=lambda k: k[1])[0][0]

    for node in nodes:
        if node.type != 'FRAME' and skipnode is False:
            locx, locy = abs_node_location(node)
            dimx = node.dimensions.x / dpifac()
            dimy = node.dimensions.y / dpifac()
            if (locx <= x <= locx + dimx) and \
                    (locy - dimy <= y <= locy):
                nodes_under_mouse.append(node)

    if len(nodes_under_mouse) == 1:
        if nodes_under_mouse[0] != nearest_node:
            target_node = nodes_under_mouse[0]  # use the node under the mouse if there is one and only one
        else:
            target_node = nearest_node  # else use the nearest node
    else:
        target_node = nearest_node
    return target_node
