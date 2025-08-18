from . import translate, icons
import os

PAINT_BUCKET_FILE_PATH = os.path.join(os.path.dirname(__file__), "icons", "PAINT_BUCKET.png")
PAINT_BUCKET_TEXTURE = None


def paint_bucket_load_texture():
    global PAINT_BUCKET_TEXTURE
    from ..utils.gpu import from_file_get_texture
    if PAINT_BUCKET_TEXTURE:
        return PAINT_BUCKET_TEXTURE
    PAINT_BUCKET_TEXTURE = from_file_get_texture(PAINT_BUCKET_FILE_PATH)
    return PAINT_BUCKET_TEXTURE

def register():
    translate.register()
    icons.register()


def unregister():
    translate.unregister()
    icons.unregister()
