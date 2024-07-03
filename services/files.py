import os
from settings import bot


async def download_files(files_list, record_id):
    path_list = []
    path = f'media/files/{record_id}'
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

    for file in files_list:
        file = await bot.get_file(file['file_id'])
        fname = file.file_path.split('/')[-1]
        file_path = path + f'/{fname}'
        await bot.download_file(file.file_path, destination=file_path)
        path_list.append(file_path)
    return path_list


async def delete_files(path_list, record_id):
    os.rmdir(f'media/files/{record_id}')
    for path in path_list:
        os.remove(path)
