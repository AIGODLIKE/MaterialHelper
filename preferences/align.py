import bpy


class Align:
    # align
    node_dis_x: bpy.props.IntProperty(name='Node Distance X', default=100, min=0, soft_max=200)
    node_dis_y: bpy.props.IntProperty(name='Node Distance Y', default=50, min=0, soft_max=100)

    def draw_align(self, layout):
        box = layout.box()
        box.label(text='Align Dependence', icon='NODETREE')
        box.prop(self, 'node_dis_x', slider=True)
        box.prop(self, 'node_dis_y', slider=True)
