import bpy


class Window:
    window_style: bpy.props.EnumProperty(name="Window Style", items=[
        ("FULL_SCREEN", "Full Screen", ""),
        ("BIG", "Big", ""),
        ("SMALL", "Small", ""),
    ], default="SMALL")

    # small_window
    show_ui_panel: bpy.props.BoolProperty(name="Show UI Panel", default=False)
    ui_direction: bpy.props.EnumProperty(name="UI Panel Direction",
                                         items=[("LEFT", "Left", ""), ("RIGHT", "Right", "")],
                                         default="RIGHT")
    use_shader_ball_preview: bpy.props.BoolProperty(
        name="Realtime Preview",
        description="If enable and open more than 15 window will crash blender",
        default=True)

    def draw_window(self, layout: bpy.types.UILayout):
        column = layout.box().column(align=True)
        column.label(text="Preview Material Window Style")

        column.separator()

        column.row(align=True).prop(self, "window_style", expand=True)

        column.separator()

        column.prop(self, "use_shader_ball_preview")
        sub_column = column.column(align=True)
        sub_column.enabled = self.use_shader_ball_preview
        sub_column.prop(self, "preview_render_type", expand=True)
        sub_column.row(align=True).prop(self, "shading_type", expand=True)

        column.separator()

        column.prop(self, "show_ui_panel")
        sub_row = column.row(align=True)
        sub_row.enabled = self.show_ui_panel
        sub_row.prop(self, "ui_direction", expand=True)
