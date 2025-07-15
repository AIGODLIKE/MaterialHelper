from . import translate, icons, material



def register():
    material.register()
    translate.register()
    icons.register()


def unregister():
    material.unregister()
    translate.unregister()
    icons.unregister()
