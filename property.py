import bpy

from .utils.mesh import from_face_index_get_material_index


class PickerMaterialItem(bpy.types.PropertyGroup):
    material: bpy.props.PointerProperty(type=bpy.types.Material)

    def draw(self, layout):
        material = self.material
        if material is not None and material.preview:
            from .ops.picker_material import MaterialAssignByItem
            layout.context_pointer_set("material", material)
            layout.context_pointer_set("picker_material", self)
            layout.operator(MaterialAssignByItem.bl_idname, icon_value=material.preview.icon_id, text="")

    def draw_active(self, layout):
        material = self.material
        if material and material.preview:
            from .ops.picker_material import MaterialAssignByItem
            layout.template_icon(material.preview.icon_id, scale=3.5)

    def assign_material(self,
                        context: bpy.types.Context,
                        obj: bpy.types.Object,
                        face_index: int,
                        assign_obj: bool = False
                        ):
        material = self.material
        material_index = from_face_index_get_material_index(obj, face_index)

        slots_len = len(obj.material_slots)
        if assign_obj or len(obj.material_slots) in (0, 1):  # 分配整个物体
            if slots_len == 0:
                with context.temp_override(object=obj):
                    bpy.ops.object.material_slot_add("INVOKE_DEFAULT", False)
            for m in obj.material_slots:
                m.material = material
        else:
            obj.material_slots[material_index].material = material


class PickerMaterial(bpy.types.PropertyGroup):
    picker_material_list: bpy.props.CollectionProperty(type=PickerMaterialItem)

    @property
    def active_material(self) -> "bpy.types.Material|None":
        if len(self.picker_material_list) != 0:
            return self.picker_material_list[0]
        return None

    def check_picker_material(self, material) -> bool:
        material_list = [m.material for m in self.picker_material_list]
        return material in material_list

    def try_picker_material(self, material: bpy.types.Material, ops=None) -> bool:
        from .utils import refresh_ui
        if material is None:
            return False

        material_list = [m.material for m in self.picker_material_list]
        if material not in material_list:
            nm = self.picker_material_list.add()
            nm.material = material
            self.picker_material_list.move(len(self.picker_material_list) - 1, 0, )
            refresh_ui(bpy.context)
            return True
        if ops is not None:
            text = bpy.app.translations.pgettext_iface("%s is pick sort to last") % material.name
            ops.report({"INFO"}, text)
        index = material_list.index(material)
        self.picker_material_list.move(index, 0, )
        return False

    def draw_picker_material(self, context, layout):
        column = layout.column(align=True)
        row_draw_len = context.region.width / 50
        if layout.scale_x != 0:
            row_draw_len *= layout.scale_x
        row_draw_len = int(row_draw_len)

        head_row = column.row(align=False)

        active_material = self.active_material
        if active_material:
            active_material.draw_active(head_row)

        head_column = head_row.column(align=True)
        row = head_column.row(align=True)

        index = 0
        column_index = 0
        for mi in self.picker_material_list:
            material = mi.material
            if material and material.preview is not None:
                is_head_column = column_index < 2
                limited_len = row_draw_len if column_index < 3 else row_draw_len + 3
                is_head_newline = is_head_column and index > limited_len
                is_n_newline = not is_head_column and index > limited_len
                if is_head_newline or is_n_newline:
                    if is_head_column:
                        row = head_column.row(align=True)
                    else:
                        row = column.row(align=True)
                    index = 0
                    column_index += 1
                mi.draw(row)
                index += 1
        if len(self.picker_material_list) == 0:
            layout.label(text="Please pick materials through the header button")

    def get_material_list(self, offset, count):
        items = [mi for mi in self.picker_material_list if mi and mi.material and mi.material.preview]
        il = len(items)
        if count > il:
            return items
        elif (offset + count) > il - 1:
            return items[offset:offset + count]
        else:
            return items[offset:offset + count]


class_tuple = (
    PickerMaterialItem,
    PickerMaterial,
)

register_class, unregister_class = bpy.utils.register_classes_factory(class_tuple)


def register():
    register_class()
    bpy.types.Scene.material_helper_property = bpy.props.PointerProperty(type=PickerMaterial)


def unregister():
    del bpy.types.Scene.material_helper_property
    unregister_class()
