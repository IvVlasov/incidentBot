import yadisk
from settings import EXCEL_PATH, DIR_PATH, YANDEX_TOKEN


y = yadisk.YaDisk(token=YANDEX_TOKEN)


class YandexDisk:

    @staticmethod
    def _create_dir(path):
        try:
            y.mkdir(path)
        except yadisk.exceptions.PathExistsError:
            # TODO добавить логгирование
            pass

    @classmethod
    def upload_excel(cls):
        cls._create_dir(DIR_PATH)
        try:
            filename = EXCEL_PATH.split('/')[-1]
            y.upload(EXCEL_PATH, DIR_PATH + '/' + filename, overwrite=True)
        except Exception:
            pass

    @classmethod
    def upload_files(cls, record_id, local_files):
        path = DIR_PATH + f'/{record_id}'
        cls._create_dir(path)
        for file in local_files:
            fname = file.split('/')[-1]
            try:
                y.upload(file, path + '/' + fname, overwrite=True)
            except Exception:
                continue
