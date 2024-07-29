from settings import bot, CHANNEL_ID, MSGS
from aiogram.utils.media_group import MediaGroupBuilder


async def send_claim_to_channel(data, chat_id):
    text = "Новая заявка: \n\n" + MSGS['admin_claim']
    text = text.format(record_id=data['record_id'],
                       chat_id=chat_id,
                       type=data['type'],
                       descr=data['descr'],
                       phone=data['phone'],
                       contact=data.get('contact', '-'))

    if len(data['files_list']) != 0:
        media = await _build_media(data['files_list'], caption=text)
        message = await bot.send_media_group(chat_id=CHANNEL_ID, media=media)
        message_id = message[0].message_id
    else:
        message = await bot.send_message(chat_id=CHANNEL_ID, text=text)
        message_id = message.message_id
    return message_id


async def _build_media(files, caption=''):
    media_group = MediaGroupBuilder(caption=caption)
    for file in files:
        if file['file_type'] == 'photo':
            media_group.add_photo(media=file['file_id'])
        if file['file_type'] == 'document':
            media_group.add_document(media=file['file_id'])
        if file['file_type'] == 'video':
            media_group.add_video(media=file['file_id'])
    return media_group.build()
