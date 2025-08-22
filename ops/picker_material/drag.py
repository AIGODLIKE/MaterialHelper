import blf
import bpy
import gpu
from bpy.app.translations import pgettext_iface
from mathutils import Vector

from .public_material import PublicMaterial
from ...utils.mesh import from_face_index_get_material_index


class MaterialDrag(bpy.types.Operator, PublicMaterial):
    bl_idname = "mathp.material_drag"
    bl_label = "Drag material"
    bl_options = {"REGISTER", "UNDO"}

    default_cursor = "HAND_CLOSED"

    def draw_handler(self, context):
        if hash(context.area) == self.start_area_hash:
            (result, material_obj, material, index) = self.start_pick_info
            (pick_result, pick_material_obj, pick_material, pick_index) = self.pick_info

            with gpu.matrix.push_pop():
                blf.position(0, 0, 0, 1)
                x, y = self.offset + Vector((50, 0))
                gpu.matrix.translate((x, y))
                texts = []
                text = material.name if material is not None else ""
                if pick_result:
                    slot_name = pgettext_iface("Material slot")
                    material_index = from_face_index_get_material_index(pick_material_obj, pick_index)
                    text += f" -> {pick_material_obj.name}({slot_name} {material_index})"
                texts.append(text)
                if pick_material:
                    texts.append(pgettext_iface("Replace material") + f" {pick_material.name}")
                self.draw_text_list(texts)

            if result and material is not None:
                self.draw_material(material)

    def start(self, context, event):
        (result, material_obj, material, index) = self.start_pick_info
        if result is False:
            self.report({"WARNING"}, "Not picker material")
            return True
        return None

    def click(self, context, event):
        import bmesh
        self.start_pick_info, self.pick_info = self.pick_info, self.start_pick_info

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
        return True
