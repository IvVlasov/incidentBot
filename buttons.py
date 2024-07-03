from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from settings import SKIP, BTNS


async def skip():
    kb = [[KeyboardButton(text=SKIP)]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


async def types(claim_types):
    builder = ReplyKeyboardBuilder()
    for button in claim_types:
        builder.button(text=button[1])
    builder.adjust(1)
    keyboard = builder.as_markup()
    keyboard.resize_keyboard = True
    keyboard.one_time_keyboard = True
    return keyboard


async def phone_btn():
    kb = [[KeyboardButton(text='Поделиться контактом', request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


async def confirm_claim_btn():
    kb = [[InlineKeyboardButton(text=BTNS['confirm_claim'], callback_data='confirm_claim')],
          [InlineKeyboardButton(text=BTNS['cancel_claim'], callback_data='cancel_claim')]]
    return InlineKeyboardMarkup(inline_keyboard=kb)


async def admin_btns():
    kb = [[InlineKeyboardButton(text='Выгрузить Excel', callback_data='load_excel')],
          [InlineKeyboardButton(text='Изменить тип обращения', callback_data='change_violations')],
          [InlineKeyboardButton(text='Найти заявку', callback_data='search_claim')],
          [InlineKeyboardButton(text='Отправить сообщение', callback_data='send_message')],
          [InlineKeyboardButton(text='Очистить Excel', callback_data='delete_excel')],
          ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


async def admin_claim_types(claim_types):
    builder = InlineKeyboardBuilder()
    for button in claim_types:
        builder.button(text=f'Удалить ID = {button[0]}', callback_data=f'delete_claim_type_{button[0]}')
    builder.button(text='Добавить тип обращения', callback_data='add_claim_type')
    builder.adjust(1)
    keyboard = builder.as_markup()
    return keyboard
