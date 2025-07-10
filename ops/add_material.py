import bpy

from pathlib import Path

class MATHP_OT_add_material(bpy.types.Operator):
    """Add Material"""
    bl_idname = "mathp.add_material"
    bl_label = "Add Material"
    bl_options = {"REGISTER", "UNDO"}

    dep_class = []  # 动态ops

    @classmethod
    def poll(cls, context):
        return hasattr(context, "selected_assets")

    def execute(self, context):
        # 清空动态注册op
        for cls in self.dep_class:
            bpy.utils.unregister_class(cls)
        self.dep_class.clear()

        # 获取材质库已有材质名
        icon_dir = Path(__file__).parent.parent.joinpath("mat_lib")
        blend_file = icon_dir.joinpath("mat.blend")
        with bpy.data.libraries.load(str(blend_file), link=False) as (data_from, data_to):
            mats = data_from.materials

        # 根据材质库材质动态注册
        def dy_modal(_self, _context, _event):
            if _event.type == "TIMER":
                if _self.count < 10:
                    _self.count += 1
                else:
                    _context.area.spaces[0].activate_asset_by_id(_self.material)
                    _context.area.tag_redraw()

                    if _self._timer:
                        _context.window_manager.event_timer_remove(_self._timer)
                        _self._timer = None
                        return {"FINISHED"}

            return {"PASS_THROUGH"}

        def dy_invoke(_self, _context, _event):
            with bpy.data.libraries.load(_self.blend_file, link=False) as (data_from, data_to):
                data_to.materials = [_self.material]

            # 刷新资产库
            bpy.ops.asset.library_refresh()
            _self.material = data_to.materials[0]
            _self._timer = _context.window_manager.event_timer_add(0.01, window=_context.window)
            _context.window_manager.modal_handler_add(_self)
            return {"RUNNING_MODAL"}

        for i, mat in enumerate(mats):
            mat_name = mat
            op_cls = type("DynOp",
                          (bpy.types.Operator,),
                          {"bl_idname": f"wm.mathp_add_material_{i}",
                           "bl_label": mat_name,
                           "bl_description": "Add",
                           # "execute": dy_execute,
                           "invoke": dy_invoke,
                           "modal": dy_modal,
                           # 自定义参数传入
                           "blend_file": str(blend_file),
                           "material": mat_name,
                           "_timer": None,
                           "count": 0
                           },
                          )
            self.dep_class.append(op_cls)

        for cls in self.dep_class:
            bpy.utils.register_class(cls)

        # 绘制动态菜单
        op = self

        def draw_custom_menu(self, context):
            global G_MAT_ICON_ID
            layout = self.layout
            layout.operator_context = "INVOKE_DEFAULT"
            for i, cls in enumerate(op.dep_class):
                o = layout.operator(cls.bl_idname, icon_value=G_MAT_ICON_ID[cls.bl_label])

        # 弹出
        context.window_manager.popup_menu(draw_custom_menu, title="Material", icon="ADD")
        return {"FINISHED"}
