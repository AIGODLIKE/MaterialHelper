import bpy


class MATHP_OT_drag_asset(bpy.types.Operator):
    bl_idname = "mathp.drag_asset"
    bl_label = "Drag"
    bl_options = {"UNDO"}
    singleton = False

    count = 0

    @classmethod
    def poll(cls, context):
        if cls.singleton:
            return False
        return True
        return hasattr(context, 'selected_assets') and context.selected_assets

    def invoke(self, context, event):
        print(self.bl_idname)
        self.__class__.singleton = True
        context.window.cursor_set("HAND_CLOSED")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        print("modal", self.bl_idname, self.count, event.value, event.type, end="\r\r")
        context.window.cursor_set("HAND_CLOSED")
        self.count += 1
        if event.value == "RELEASE" and event.type == "LEFTMOUSE":
            self.exit(context)
            return {"FINISHED"}
        elif self.count == 1:
            return {"PASS_THROUGH"}
        return {"RUNNING_MODAL"}

    def exit(self, context):
        print("exit")
        self.__class__.singleton = False
        context.window.cursor_set("DEFAULT")
        self.count = 0
