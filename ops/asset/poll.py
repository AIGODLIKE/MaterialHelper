class AssetPoll:
    @classmethod
    def poll(cls, context):
        """context.area.ui_type context.area.type
        ASSETS FILE_BROWSER
        FILES FILE_BROWSER
        """
        if hasattr(context, "selected_assets") and context.selected_assets and context.area.ui_type == "ASSETS":
            return True
        return False
