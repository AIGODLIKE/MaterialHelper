import bpy
import rna_keymap_ui

from .material import Material
from .. import __package__ as base_package


class MaterialHelperPreference(bpy.types.AddonPreferences, Material):
    bl_idname = base_package

    ui: bpy.props.EnumProperty(name='UI', items=[
        ('SETTINGS', 'Settings', '', 'PREFERENCES', 0),
        ('KEYMAP', 'Keymap', '', 'KEYINGSET', 1),
    ], default='SETTINGS')

    # big_window

    # general window setting
    shader_ball: bpy.props.EnumProperty(name='Shader Ball',
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
    shading_type: bpy.props.EnumProperty(name='Shading',
                                         items=[
                                             ('SOLID', 'Solid', ''),
                                             ('MATERIAL', 'Material', '', 'SHADING_SOLID', 1),
                                             ('RENDERED', 'Rendered', '', 'SHADING_RENDERED', 2),
                                         ], default='MATERIAL')

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
        row.prop(self, 'show_text', expand=True)

        self.draw_window(box)

        col.separator()
        self.draw_align(col)

    def draw_keymap(self, context, layout):
        col = layout.box().column()
        col.label(text="Keymap", icon="KEYINGSET")
        km = None
        wm = context.window_manager
        kc = wm.keyconfigs.user

        old_km_name = ""
        get_kmi_l = []

        from ..keymaps import addon_keymaps

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
    bpy.utils.register_class(MaterialHelperPreference)


def unregister():
    bpy.utils.unregister_class(MaterialHelperPreference)
