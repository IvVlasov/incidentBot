from typing import List
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram_media_group import media_group_handler
from aiogram.enums import ParseMode
from settings import MSGS, BTNS, SKIP, SMTP_ENABLE
from handlers.states import Violation
from services import database, excel, mail, files, channel
from services.yandex import YandexDisk
import buttons


user_router = Router()


@user_router.message(F.text == '/start')
async def start(message: types.Message, state: FSMContext):
    database.User(message.chat).create_user()
    text = MSGS['start']
    kb = [[types.InlineKeyboardButton(text=BTNS['start_menu'], callback_data='start_menu')]]
    await message.answer(text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=kb))
    await state.clear()


@user_router.message(F.text == '/narushenie')
async def violation_command(message: types.Message, state: FSMContext):
    await state.clear()
    claim_types = database.ClaimTypes.get_all()
    btn = await buttons.types(claim_types)
    text = MSGS['choose_violation']
    await message.answer(text, reply_markup=btn)
    await state.set_state(Violation.s1)


@user_router.callback_query(F.data == 'start_menu')
async def start_menu(call: types.CallbackQuery, state: FSMContext):
    await violation_command(call.message, state)


@user_router.message(Violation.s1)
async def _type(message: types.Message, state: FSMContext):
    claim_types = database.ClaimTypes.get_all()
    claim_types_ls = [el[1] for el in claim_types]
    if message.text not in claim_types_ls:
        text = MSGS['steps']['choose_err']
        await message.answer(text)
        return
    await state.update_data(type=message.text)
    text_1 = MSGS['steps']['start']
    await message.answer(text_1)
    text_2 = MSGS['steps']['descr']
    await message.answer(text_2)
    await state.set_state(Violation.s2)


@user_router.message(F.text, Violation.s2)
async def place_text(message: types.Message, state: FSMContext):
    await state.update_data(descr=message.text)
    user = database.User(message.chat).get_user()
    # Если номер телефона указан -> переходим сразу к следующему шагу
    if user[3]:
        await state.update_data(phone=user[3])
        await phone_next(message, state)
        return
    text = MSGS['steps']['phone']
    btn = await buttons.phone_btn()
    await message.answer(text, reply_markup=btn)
    await state.set_state(Violation.s3)


@user_router.message(F.contact, Violation.s3)
async def phone_contact(message: types.Message, state: FSMContext):
    database.User(message.chat).update_phone(message.contact.phone_number)
    await state.update_data(phone=message.contact.phone_number)
    await phone_next(message, state)


@user_router.message(F.text, Violation.s3)
async def phone_text(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await phone_next(message, state)


async def phone_next(message: types.Message, state: FSMContext):
    text = MSGS['steps']['contact']
    btn = await buttons.skip()
    await message.answer(text, reply_markup=btn)
    await state.set_state(Violation.s4)


@user_router.message(F.text, Violation.s4)
async def contact_text(message: types.Message, state: FSMContext):
    if message.text != SKIP:
        await state.update_data(contact=message.text)
    text = MSGS['steps']['imgs']
    btn = await buttons.skip()
    await message.answer(text, reply_markup=btn)
    await state.set_state(Violation.s5)


@user_router.message(Violation.s5)
@media_group_handler(only_album=False)
async def media_files(messages:  List[types.Message], state: FSMContext):
    files = []
    for message in messages:
        if message.photo:
            files.append({'file_type': 'photo', 'file_id': message.photo[-1].file_id})
        if message.document:
            files.append({'file_type': 'document', 'file_id': message.document.file_id})
        if message.video:
            files.append({'file_type': 'video', 'file_id': message.video.file_id})
    await state.update_data(files_list=files)
    await send_confirm_msg(message, state)


async def send_confirm_msg(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = MSGS['steps']['confirm']
    text = text.format(type=data['type'],
                       count=len(data['files_list']),
                       descr=data['descr'],
                       phone=data['phone'],
                       contact=data.get('contact', '-'))
    btn = await buttons.confirm_claim_btn()
    await message.answer(text, reply_markup=btn)
    await state.set_state(Violation.s6)


@user_router.callback_query(F.data == 'confirm_claim')
async def confirm_claim(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await call.message.edit_reply_markup()
    record_id = database.Claim.create(call.message.chat.id, data)
    text = MSGS['steps']['finish'].format(number=record_id)
    await call.message.answer(text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=types.ReplyKeyboardRemove())

    data['record_id'] = record_id
    # Отправляем заявку в channel
    msg_id = await channel.send_claim_to_channel(data, call.message.chat.id)
    database.Claim.update_message_id(record_id, msg_id)
    # Вставляем в excel заявку
    excel.ExcelFile.paste_in_excel(data, call.message.chat.id)
    # Обновляем Excel на Яндекс диске
    YandexDisk.upload_excel()

    path_list = []
    if len(data['files_list']) != 0:
        # Сохраняем файлы в бд
        database.Files.add(data['files_list'], data['record_id'])
        # Загружаем файлы локально
        path_list = await files.download_files(data['files_list'], data['record_id'])
        # Отправляем файлы в яндекс
        YandexDisk.upload_files(data['record_id'], path_list)
        # await files.delete_files(path_list, data['record_id'])

    if SMTP_ENABLE:
        # Отправляем заявку на почту
        mail.send_claim(call.message.chat.id, data, path_list)


@user_router.callback_query(F.data == 'cancel_claim')
async def cancel_claim(call: types.CallbackQuery, state: FSMContext):
    await start_menu(call, state)
