from aiogram import Bot,Router
from aiogram.types import Message

import config

admin_router = Router()

@admin_router.message()
async def all_messages(message: Message,bot: Bot,):
    msg_text = (
        f"Пользователь: "
        f"{message.from_user.full_name} написал:\n"
        f"{message.text or 'Сообщение без текста'}"
    )

    await bot.send_message(
        chat_id=config.ADMIN_ID,
        text=msg_text,
    )