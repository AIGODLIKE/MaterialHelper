import os
from pathlib import Path
from typing import Optional


def get_blend_file(name: str) -> Optional[Path]:
    fullname = name if name.endswith('.blend') else name + '.blend'
    fp = Path(__file__).parent.joinpath('statics', 'blend_file', fullname)
    return fp if fp.exists() else None


def get_images_dir() -> Path:
    return Path(__file__).joinpath('statics', 'images')
