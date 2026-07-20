import os
import shutil
import zipfile


def extract_tickets(zip_path, tickets_folder):
    """
    Распаковывает ZIP с билетами.
    Полностью очищает папку tickets перед распаковкой.
    """

    # если папки нет — создаем
    os.makedirs(tickets_folder, exist_ok=True)

    # очищаем старые pdf
    for file in os.listdir(tickets_folder):
        path = os.path.join(tickets_folder, file)

        if os.path.isfile(path):
            os.remove(path)

    # распаковываем
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(tickets_folder)

    # убираем лишние папки, если ZIP был создан с вложенной директорией
    for root, dirs, files in os.walk(tickets_folder):
        if root == tickets_folder:
            continue

        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(tickets_folder, file)
            shutil.move(src, dst)

    # удаляем пустые папки
    for root, dirs, files in os.walk(tickets_folder, topdown=False):
        if root != tickets_folder:
            os.rmdir(root)

    return True