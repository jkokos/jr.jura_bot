from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile

from keyboards import keyboard_main_menu
from utils import FileManager
from utils.enum_path import Path

start_router = Router()

@start_router.message(Command("start"))
async def command_handler(message: Message,state: FSMContext,):
    await state.clear()

    await message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="start")
        ),
        caption=FileManager.read_txt(
            Path.MESSAGES,
            "start",
        ),
        reply_markup=keyboard_main_menu(),
    )