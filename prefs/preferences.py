import bpy
import rna_keymap_ui
from .. import __ADDON_NAME__
from bpy.props import EnumProperty, StringProperty, IntProperty, BoolProperty, PointerProperty
from bpy.types import PropertyGroup


class WindowStyleProperty(PropertyGroup):
    show_UI: BoolProperty(name='Show UI Panel')
    UI_direction: EnumProperty(name='UI Panel Direction', items=[('LEFT', 'Left', ''), ('RIGHT', 'Right', '')])


class WindowStyleProperty2(PropertyGroup):
    shader_ball: EnumProperty(name='Shader Ball',
                              items=[
                                  ('NONE', 'Follow Material', ''),
                                  ('FLAT', 'Flat', ''),
                                  ('SPHERE', 'Sphere', ''),
                                  ('CUBE', 'Cube', ''),
                                  ('HAIR', 'Hair', ''),
                                  ('SHADERBALL', 'Shader Ball', ''),
                                  ('CLOTH', 'Cloth', ''),
                                  ('FLUID', 'Fluid', ''),
                              ],
                              default='NONE')
    shading_type: EnumProperty(name='Shading',
                               items=[
                                   ('SOLID', 'Solid', ''),
                                   ('MATERIAL', 'Material', '', 'SHADING_SOLID', 1),
                                   ('RENDERED', 'Rendered', '', 'SHADING_RENDERED', 2),
                               ], default='MATERIAL')


class MATHP_Preference(bpy.types.AddonPreferences):
    bl_idname = __ADDON_NAME__

    ui: EnumProperty(name='UI', items=[
        ('SETTINGS', 'Settings', '', 'PREFERENCES', 0),
        ('KEYMAP', 'Keymap', '', 'KEYINGSET', 1),
    ], default='SETTINGS')

    window_style: EnumProperty(name='Material Window', items=[
        ('1', 'Big Window', ''),
        ('2', 'Small Window', ''),
    ], default='1')

    small_window: PointerProperty(type=WindowStyleProperty)

    big_window: PointerProperty(type=WindowStyleProperty2)

    node_dis_x: IntProperty(name='Node Distance X', default=100, min=0, soft_max=200)
    node_dis_y: IntProperty(name='Node Distance Y', default=50, min=0, soft_max=100)

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.prop(self, 'ui', expand=True)

        if self.ui == 'KEYMAP':
            self.draw_keymap(context, layout)
        elif self.ui == 'SETTINGS':
            self.draw_settings(context, layout)

    def draw_settings(self, context, layout):
        col = layout.column()
        col.use_property_split = True

        box = col.box()
        box.label(text='Edit Material Asset', icon='MATERIAL')
        row = box.row(align=True)
        row.prop(self, 'window_style', expand=True)

        if self.window_style == '1':
            w = self.big_window
            subcol = box.column()
            subcol.prop(w, 'shader_ball')
            subrow = subcol.row(align=True)
            subrow.prop(w, 'shading_type', expand=True)

        elif self.window_style == '2':
            w = self.small_window
            subcol = box.column()
            subcol.prop(w, 'show_UI')
            subcol.prop(w, 'UI_direction')

        col.separator()

        box = col.box()
        box.label(text='Align Dependence', icon='NODETREE')
        box.prop(self, 'node_dis_x', slider=True)
        box.prop(self, 'node_dis_y', slider=True)

    def draw_keymap(self, context, layout):
        col = layout.box().column()
        col.label(text="Keymap", icon="KEYINGSET")
        km = None
        wm = context.window_manager
        kc = wm.keyconfigs.user

        old_km_name = ""
        get_kmi_l = []

        from .data_keymap import addon_keymaps

        for km_add, kmi_add in addon_keymaps:
            for km_con in kc.keymaps:
                if km_add.name == km_con.name:
                    km = km_con
                    break

            for kmi_con in km.keymap_items:
                if kmi_add.idname == kmi_con.idname and kmi_add.name == kmi_con.name:
                    get_kmi_l.append((km, kmi_con))

        get_kmi_l = sorted(set(get_kmi_l), key=get_kmi_l.index)

        for km, kmi in get_kmi_l:
            if not km.name == old_km_name:
                col.label(text=str(km.name), icon="DOT")

            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)

            old_km_name = km.name


def register():
    bpy.utils.register_class(WindowStyleProperty)
    bpy.utils.register_class(WindowStyleProperty2)
    bpy.utils.register_class(MATHP_Preference)


def unregister():
    bpy.utils.unregister_class(MATHP_Preference)
    bpy.utils.unregister_class(WindowStyleProperty)
    bpy.utils.unregister_class(WindowStyleProperty2)
