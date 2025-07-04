import bpy
from ..ops.tmp_asset import update_user_control


def update_shader_ball(self, context):
    from ..ops.edit_material_asset import set_shader_ball_mat
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
    # 防止多个操作符同时运行 MATHP_OT_align_dependence
    bpy.types.WindowManager.mathp_node_move = bpy.props.BoolProperty(default=False)
    bpy.types.WindowManager.mathp_node_anim = bpy.props.BoolProperty(default=False)

    bpy.types.WindowManager.mathp_global_update = bpy.props.BoolProperty(name='Update', default=False)
    bpy.types.Material.mathp_preview_render_type = bpy.props.EnumProperty(name='Shader Ball',
                                                                          items=[
                                                                              ('FLAT', 'Flat', '', 'MATPLANE', 0),
                                                                              ('SPHERE', 'Sphere', '', 'MATSPHERE', 1),
                                                                              ('CUBE', 'Cube', '', 'MATCUBE', 2),
                                                                              ('HAIR', 'Hair', '', 'CURVES', 3),
                                                                              ('SHADERBALL', 'Shader Ball', '',
                                                                               'MATSHADERBALL',
                                                                               4),
                                                                              ('CLOTH', 'Cloth', '', 'MATCLOTH', 5),
                                                                              ('FLUID', 'Fluid', '', 'MATFLUID', 6),
                                                                          ], default='SPHERE',
                                                                          update=update_shader_ball)

    # 用户总控制开关
    bpy.types.Scene.mathp_update_mat = bpy.props.BoolProperty(name='Auto Update',
                                                              default=True,
                                                              description='If checked, the material will be automatically add as temp asset\nElse, temp assets will be cleared',
                                                              update=update_user_control)
    bpy.types.WindowManager.mathp_update_active_obj_mats = bpy.props.BoolProperty(name='Object / Material Select Sync',
                                                                                  description="If checked, the active object's materials will be automatically selected",
                                                                                  default=False)


def unregister():
    del bpy.types.WindowManager.mathp_node_move
    del bpy.types.WindowManager.mathp_node_anim

    del bpy.types.WindowManager.mathp_global_update
    del bpy.types.Material.mathp_preview_render_type

    del bpy.types.Scene.mathp_update_mat
    del bpy.types.WindowManager.mathp_update_active_obj_mats
