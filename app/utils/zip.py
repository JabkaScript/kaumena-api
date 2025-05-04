import datetime
import os
import zipfile

def zip_folder(folder_path: str, zip_path: str):
    """
    Упаковывает содержимое папки `folder_path` в архив `zip_path`
    """

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".zip"):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                zipf.write(file_path, arcname)

    return zip_path