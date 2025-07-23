from . import translate, icons



def register():
    translate.register()
    icons.register()


def unregister():
    translate.unregister()
    icons.unregister()
