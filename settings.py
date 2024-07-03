import json
import configparser
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


# Загружаем текста сообщений и кнопок
json_file = json.load(open('config/messages.json', encoding='utf-8'))
MSGS = json_file['messages']
BTNS = json_file['buttons']

# Загружаем и парсим основной конфиг
config = configparser.ConfigParser()
config.read('config/config.ini', encoding='utf-8')
TOKEN = config['bot']['token']
DB_PATH = config['bot']['db_path']
CLAIM_LENGTH = int(config['bot']['lenght'])
SKIP = 'Пропустить'
ADMIN_IDS = config['bot']['adminId'].split(',')
CHANNEL_ID = config['bot']['channelId']

# Настройки Яндекса и Excel
EXCEL_PATH = config['yandex']['excel_path']
DIR_PATH = config['yandex']['dir_path']
YANDEX_TOKEN = config['yandex']['token']

# Настройки SMTP
SMTP_ENABLE = int(config['mail']['enable'])
SMTP_SERVER = config['mail']['server']
SMTP_USER = config['mail']['user']
SMTP_PASSWORD = config['mail']['password']
SMTP_SEND_TO = config['mail']['send_to']


# Создание диспатчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
