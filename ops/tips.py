import bpy


class Tips(bpy.types.Operator):
    bl_idname = "mathp.tips"
    bl_label = "Tips"

    tips: bpy.props.StringProperty()
    type: bpy.props.StringProperty(default="WARNING")

    def execute(self, context):
        self.report({self.type}, self.tips)
        return {"FINISHED"}
