import bpy


def get_pref() -> bpy.types.AddonPreferences:
    """get preferences of this plugin"""
    return bpy.context.preferences.addons.get(__package__).preferences
