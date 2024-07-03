from aiogram import types, Router, F
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from settings import ADMIN_IDS, MSGS, EXCEL_PATH
import buttons
from services import database, admin, excel, yandex
from handlers.states import Admin
import os


class AdminFilter(Filter):
    async def __call__(self, msg) -> bool:
        if isinstance(msg, types.Message):
            return str(msg.chat.id) in ADMIN_IDS
        if isinstance(msg, types.CallbackQuery):
            return str(msg.message.chat.id) in ADMIN_IDS


admin_router = Router()


@admin_router.message(AdminFilter(), F.text == '/admin')
async def admin_start(message: types.Message, state: FSMContext):
    await state.clear()
    txt = 'Выберите действие'
    btn = await buttons.admin_btns()
    await message.answer(txt, reply_markup=btn)


@admin_router.callback_query(AdminFilter(), F.data == 'load_excel')
async def download_excel(call: types.CallbackQuery, state: FSMContext):
    doc = FSInputFile(EXCEL_PATH)
    await call.message.answer_document(document=doc)


@admin_router.callback_query(AdminFilter(), F.data == 'change_violations')
async def change_violations(call: types.CallbackQuery, state: FSMContext):
    claim_types = database.ClaimTypes.get_all()
    text = ''
    for claim in claim_types:
        text += f"ID: {claim[0]}. Текст: {claim[1]}\n\n"

    btn = await buttons.admin_claim_types(claim_types)
    await call.message.answer(text, reply_markup=btn)


@admin_router.callback_query(AdminFilter(), F.data == 'add_claim_type')
async def add_claim_type(call: types.CallbackQuery, state: FSMContext):
    text = 'Введите название нового типа обрщения'
    await call.message.answer(text)
    await state.set_state(Admin.add_claim)


@admin_router.message(AdminFilter(), Admin.add_claim)
async def add_claim(message: types.Message, state: FSMContext):
    text = message.text
    database.ClaimTypes.add(text)
    await message.answer('Обрщение успешно добавлено!')
    await state.clear()


@admin_router.callback_query(AdminFilter(), F.data.startswith('delete_claim_type_'))
async def delete_claim_type(call: types.CallbackQuery, state: FSMContext):
    value = call.data.split('_')[-1]
    database.ClaimTypes.delete(value)
    await call.message.answer('Обрщение успешно удалено!')
    await state.clear()


@admin_router.callback_query(AdminFilter(), F.data == 'search_claim')
async def search_claim(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('Введите номер заявки')
    await state.set_state(Admin.search_claim)


@admin_router.message(AdminFilter(), Admin.search_claim)
async def search_claim_number(message: types.Message, state: FSMContext):
    value = message.text.replace('#', '')
    row = database.Claim.get_full_claim(value)
    if not row:
        await message.answer('Не удалось найти заявку')
        await state.clear()
        return

    text = MSGS['admin_claim']
    text = text.format(record_id=row[0],
                       chat_id=row[1],
                       type=row[2],
                       descr=row[3],
                       phone=row[-1],
                       contact=row[4])
    files = database.Files.get(row[0])
    if not files:
        await message.answer(text)
        return

    files_dict = [{'file_id': el[2], 'file_type': el[3]} for el in files]
    media = await admin._build_media(files_dict, caption=text)
    await message.answer_media_group(media)


@admin_router.callback_query(AdminFilter(), F.data == 'delete_excel')
async def delete_excel(call: types.CallbackQuery, state: FSMContext):
    try:
        os.remove(EXCEL_PATH)
    except OSError:
        pass
    excel.ExcelFile.create_excel()
    yandex.YandexDisk.upload_excel()
    await call.message.answer('Excel был удален')


@admin_router.callback_query(AdminFilter(), F.data == 'send_message')
async def send_message(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('Введите ID пользователя, которому необхоидмо отправить сообщение')
    await state.set_state(Admin.send_message)


@admin_router.message(AdminFilter(), Admin.send_message)
async def send_message_user(message: types.Message, state: FSMContext):
    chat_id = message.text
    user = database.User.get_user_by_id(chat_id)
    if not user:
        await message.answer('Не удалось найти пользователя')
        return
    await message.answer('Пользователь найден! Напишите сообщение, которое необходимо ему отправить')
    await state.update_data(chat_id=chat_id)
    await state.set_state(Admin.send_message_msg)


@admin_router.message(AdminFilter(), Admin.send_message_msg)
async def send_message_msg(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.copy_to(data['chat_id'])
