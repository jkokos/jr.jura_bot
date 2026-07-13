from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message


main_router = Router()


@main_router.message(Command('start'))
async def start_command(message):
    print(message)

@main_router.message()
async def all_message(message:Message, bot:Bot):
    msg_text = f'пользователь: {message.from_user.full_name} написал:\n {message.text}'
    await bot.send_message(
        chat_id=418087860,
        text=str(),
    )

