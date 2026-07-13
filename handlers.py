from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from keyboards import keyboard_main_menu
import config
main_router = Router()


@main_router.message(Command('start')) #start
async def start_command(message:Message):
    await message.answer(
        text = f'Hello {message.from_user.full_name}! \n Ready',
        reply_markup=keyboard_main_menu(),
    )

@main_router.message(Command('random'))
async def random_command(message):
    print(message.from_user.id)


@main_router.message()
async def all_messages(message:Message, bot:Bot):   # otvet v telege
    msg_text = f'пользователь: {message.from_user.full_name} написал:\n {message.text}'

    await bot.send_message(
        chat_id=config.ADMIN_ID,
        text=msg_text,
    )

