import blf
import bmesh
import bpy
import gpu.matrix
from bpy.app.translations import pgettext_iface
from mathutils import Vector

from .public_material import PublicMaterial
from ...utils.translate import translate_lines_text


class MaterialPicker(bpy.types.Operator, PublicMaterial):
    bl_idname = "mathp.material_picker"
    bl_label = "Picker Material"
    bl_options = {"REGISTER"}

    picker_all_selected: bpy.props.BoolProperty(options={"SKIP_SAVE"})
    picker_to_select: bpy.props.BoolProperty(default=False, options={"SKIP_SAVE"})

    header_text = "Ctrl:Continuous pick    Alt:Pick object all material"

    @classmethod
    def description(cls, context, properties):
        if properties.picker_all_selected:
            return translate_lines_text("Picker the materials of all selected objects")
        return translate_lines_text(
            "\n",
            "Ctrl: Pick all material in asset",
            "Shift: Picker the materials of all selected objects",
            "Alt: Pick all materials in the scene",
        )

    @property
    def pick_hub_text(self) -> str:
        text = "None"
        (result, material_obj, material, index) = self.pick_info
        if result:
            text = f"{material_obj.name}"
            if material is not None:
                text += f" -> {material.name}"
        return text

    def draw_handler_texts(self, context):
        (start_result, start_material_obj, start_material, start_index) = self.start_pick_info
        x, y = self.offset + Vector((50, 0))
        with gpu.matrix.push_pop():
            blf.position(0, 0, 0, 1)
            gpu.matrix.translate((x, y))

            texts = [
                pgettext_iface("Picker Material"),
            ]

            objects_name = list((i.name for i in context.selected_objects))
            select_count = len(objects_name)
            if self.picker_to_select:
                if start_result:
                    face_index = pgettext_iface("Face Index")
                    assign = pgettext_iface("Assign material")
                    text = f"{assign}: {start_material_obj.name} -> {face_index}:{start_index}"
                    texts.append(text)
                elif select_count:
                    text = pgettext_iface("Assign material to %i objects %s")
                    texts.append(text % (select_count, ""))
            else:
                event = self.event
                if event.alt:
                    texts.append(pgettext_iface("Picker the materials of all selected objects"))
                if event.ctrl:
                    texts.append(pgettext_iface("Continuous picker material"))
            texts.append(self.pick_hub_text)
            self.draw_text_list(texts)

    def draw_handler(self, context):
        if hash(context.area) == self.start_area_hash:
            (result, material_obj, material, index) = self.pick_info
            self.draw_handler_texts(context)
            if result and material is not None:
                self.draw_material(material)

    def start(self, context, event):
        material_helper_property = context.scene.material_helper_property
        self.update(context, event)
        if self.picker_to_select:  # 拾取材质到所有选中的物体
            (start_result, start_material_obj, start_material, start_index) = self.start_pick_info
            self.continuous = False
            if start_result:
                text = bpy.app.translations.pgettext_iface("Assign picker material to %s -> %i")
                self.header_text = text % (start_material_obj.name, start_index)
            else:
                text = bpy.app.translations.pgettext_iface("Assign picker material to %i objects %s")
                objects_name = list((i.name for i in context.selected_objects))
                self.header_text = text % (len(objects_name), ",".join(objects_name))
        elif event.shift or self.picker_all_selected:  # 拾取所有选择物体材质
            count = 0
            for obj in context.selected_objects:
                if obj.type == "MESH":
                    for material in obj.data.materials:
                        if material_helper_property.try_picker_material(material, None):
                            count += 1
            text = bpy.app.translations.pgettext_iface("%i materials have been picker") % count
            self.report({"INFO"}, text)
            return True
        elif event.ctrl:  # 拾取所有资产
            for mat in bpy.data.materials:
                if mat.asset_data:
                    material_helper_property.try_picker_material(mat, None)
            return True
        elif event.alt:  # 拾取所有场景材质
            count = 0
            for obj in context.scene.objects:
                if obj.type == "MESH":
                    for material in obj.data.materials:
                        if material_helper_property.try_picker_material(material, None):
                            count += 1

            text = bpy.app.translations.pgettext_iface("%i materials have been picker") % count
            self.report({"INFO"}, text)
            return True

    def click(self, context, event):
        """拾取材质
        在按下左键时"""
        result, material_obj, material, index = self.pick_info
        material_helper_property = context.scene.material_helper_property
        pgettext_iface = bpy.app.translations.pgettext_iface
        if result:
            text = self.pick_hub_text
            if self.picker_to_select:  # 拾取材质到所有选择物体
                if t := self.assign_to_select(context, event): text = t
            elif event.alt:  # 拾取所有物体的材质
                picker_count = 0
                for material in material_obj.data.materials:
                    if material is not None:
                        if material_helper_property.try_picker_material(material, self):
                            picker_count += 1
                text = pgettext_iface("Picker material: %i") % picker_count
            elif material_obj:
                if material is not None:
                    material_helper_property.try_picker_material(material, self)

            not_modify = (not event.alt) and (not event.ctrl) and (not event.shift)
            if len(context.selected_objects) != 0 and not_modify:
                if active_material := context.scene.material_helper_property.active_material:
                    for obj in context.selected_objects:
                        if obj.type == "MESH":
                            active_material.assign_material(context, obj, -1, True)
        else:
            text = pgettext_iface("Material not picked up")

        self.report({"INFO"}, text)

    def assign_to_select(self, context, event):
        result, material_obj, material, index = self.pick_info
        material_helper_property = context.scene.material_helper_property
        material_helper_property.try_picker_material(material, self)
        active_material = material_helper_property.active_material
        if active_material:
            start_result, start_material_obj, _, start_index = self.start_pick_info
            if start_result:
                if context.mode == "EDIT_MESH":
                    bm = bmesh.from_edit_mesh(start_material_obj.data)
                    if bm.faces[start_index].select:
                        from .assign_by_item import MaterialAssignByItem
                        for obj in context.selected_objects:
                            if obj.type == "MESH":
                                MaterialAssignByItem.assign_to_select_face(context, obj, active_material.material)
                active_material.assign_material(context, start_material_obj, start_index, assign_obj=False)
                material_name = active_material.material.name if active_material.material is not None else None
                return f"{start_material_obj.name} -> {start_index} -> {material_name}"
            else:
                objects_name = []
                for obj in context.selected_objects:
                    objects_name.append(obj.name)
                    active_material.assign_material(context, obj, 0, assign_obj=True)
                return f"{active_material.material.name} -> {objects_name.__repr__()}"
        return None
