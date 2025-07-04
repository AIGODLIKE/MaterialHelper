import bpy


class MATHP_MT_asset_browser_menu(bpy.types.Menu):
    bl_label = 'Material Helper'
    bl_idname = 'MATHP_MT_asset_browser_menu'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'

        layout.separator()
        layout.operator('mathp.clear_unused_material', icon='X')

        layout.separator()

        layout.operator('mathp.add_material', icon='ADD')
        layout.operator('mathp.duplicate_asset')
        layout.operator('mathp.rename_asset')
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator('mathp.replace_mat')
        layout.operator('mathp.delete_asset')
        layout.separator()

        layout.operator('mathp.set_true_asset', icon='ASSET_MANAGER')
