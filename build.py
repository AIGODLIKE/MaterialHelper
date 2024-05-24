from pathlib import Path


def build_addon_zip_file(zip_dir: Path, dest_zip_path: Path) -> tuple[bool, str]:
    """
    :param zip_dir:
    :param dest_zip_path:
    :return:
        bool: success
        str: dest_zip_path/err_msg
    """
    import shutil, os
    import zipfile

    def prepare_files():
        temp_dir = dest_zip_path.parent.joinpath('BME_TMP_ZIP')
        sub_dir = temp_dir.joinpath(dest_zip_path.stem)
        if sub_dir.exists():
            shutil.rmtree(sub_dir)
        sub_dir.mkdir(parents=True)

        for file in zip_dir.glob('*'):
            if file.is_dir():
                if file.name.startswith('__') or file.name.startswith('.') or file == 'dist': continue
                shutil.copytree(file, sub_dir.joinpath(file.name))

            elif file.is_file():
                if file.name == __file__: continue

                shutil.copy(file, sub_dir.joinpath(file.name))

        return temp_dir

    try:
        temp_dir = prepare_files()
        with zipfile.ZipFile(dest_zip_path, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zip:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    zip.write(os.path.join(root, file),
                              arcname=os.path.join(root, file).replace(str(temp_dir), ''))
        shutil.rmtree(temp_dir)

        return True, f'{dest_zip_path}'
    except Exception as e:
        return False, str(e)


if __name__ == '__main__':
    dest_zip_path = Path(__file__).parent.joinpath('dist', 'MaterialHelper.zip')
    zip_dir = Path(__file__).parent
    res, msg = build_addon_zip_file(zip_dir, dest_zip_path)
    print(res, msg)
