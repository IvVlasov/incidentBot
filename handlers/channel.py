from aiogram import types, Router, F
from services.database import Claim
from settings import bot, CHANNEL_ID
from typing import List
from aiogram.enums import ParseMode
from aiogram_media_group import media_group_handler


channel_router = Router()


@channel_router.channel_post(F.photo or F.document or F.video)
@media_group_handler(only_album=False)
async def parse_media(messages: List[types.Message]):
    messages_ids = [msg.message_id for msg in messages]
    reply = messages[0].reply_to_message
    if reply:
        claim = Claim.get_claim_by_message_id(reply.message_id)
        await edit_text(claim, messages[0], True)
        await send_answer_to_user(claim, messages_ids)


@channel_router.channel_post(F.text)
async def parse(message: types.Message):
    reply = message.reply_to_message
    if reply:
        message_id = reply.message_id
        claim = Claim.get_claim_by_message_id(message_id)
        await edit_text(claim, message, False)
        await send_answer_to_user(claim, [message.message_id])


async def edit_text(claim, message: types.Message, is_caption: bool):
    if is_caption:
        new_caption = f"*Ответ на заявку* `\#{claim[0]}`\n\n{message.caption}"
        await bot.edit_message_caption(chat_id=CHANNEL_ID,
                                       parse_mode=ParseMode.MARKDOWN_V2,
                                       message_id=message.message_id,
                                       caption=new_caption)
    else:
        new_text = f"*Ответ на заявку* `\#{claim[0]}`\n\n{message.text}"
        await bot.edit_message_text(chat_id=CHANNEL_ID,
                                    parse_mode=ParseMode.MARKDOWN_V2,
                                    message_id=message.message_id,
                                    text=new_text)


async def send_answer_to_user(claim, channel_msg_ids):
    await bot.copy_messages(chat_id=claim[1],
                            from_chat_id=CHANNEL_ID,
                            message_ids=channel_msg_ids)
