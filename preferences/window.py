import bpy


class Window:
    window_style: bpy.props.EnumProperty(name='Material Window', items=[
        ('BIG', 'Big Window', ''),
        ('SMALL', 'Small Window', ''),
    ], default='1')

    # small_window
    show_UI: bpy.props.BoolProperty(name='Show UI Panel')
    UI_direction: bpy.props.EnumProperty(name='UI Panel Direction',
                                         items=[('LEFT', 'Left', ''), ('RIGHT', 'Right', '')],
                                         default='RIGHT')
    use_shader_ball_pv: bpy.props.BoolProperty(
        name='Realtime Preview(If enable and open more than 15 window will crash blender)',
        default=False)

    def draw_window(self, layout: bpy.types.UILayout):
        box = layout.box()
        row = box.row()
        row.prop(self, 'window_style', expand=True)
        if self.window_style == 'BIG':
            subcol = box.column()
            subcol.prop(self, 'shader_ball')
            subrow = subcol.row(align=True)
            subrow.prop(self, 'shading_type', expand=True)
        elif self.window_style == 'SMALL':
            subcol = box.column()
            subcol.prop(self, 'show_UI')
            subcol.prop(self, 'UI_direction')

            subcol = box.column()
            subcol.prop(self, 'use_shader_ball_pv')
            if self.use_shader_ball_pv:
                subcol = box.column()
                subcol.prop(self, 'shader_ball')
                subrow = subcol.row(align=True)
                subrow.prop(self, 'shading_type', expand=True)
