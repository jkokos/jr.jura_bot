from aiogram import Bot,F,Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery,Message
from aiogram.types.input_file import FSInputFile

from ai_open import chat_gpt
from ai_open.gpt_messages import GPTMessage
from handlers.gpt.states import GPTState

from keyboards import keyboard_gpt, keyboard_main_menu

from utils import FileManager
from utils.enum_path import Path

gpt_router = Router()

@gpt_router.callback_query(F.data == "gpt")
async def gpt_button(callback: CallbackQuery,state: FSMContext,):
    await callback.answer()
    await state.set_state(GPTState.waiting_question)

    await callback.message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="gpt")
        ),
        caption="Напиши вопрос для GPT:",
        reply_markup=keyboard_gpt(),
    )

@gpt_router.message(Command("gpt"))
async def gpt_command(message: Message,state: FSMContext,):
    await state.set_state(GPTState.waiting_question)

    await message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="gpt")
        ),
        caption="Напиши вопрос для GPT:",
        reply_markup=keyboard_gpt(),
    )

@gpt_router.message(GPTState.waiting_question)
async def gpt_answer(message: Message,bot: Bot,):
    if not message.text:
        await message.answer("Задай вопрос.")
        return

    await message.answer("Думаю...")

    gpt_message = GPTMessage("gpt")
    gpt_message.message_list.append({
        "role": "user",
        "content": message.text,
    })

    response = await chat_gpt.request(
        gpt_message,
        bot,
    )

    await message.answer(
        response,
        reply_markup=keyboard_gpt(),
    )

@gpt_router.callback_query(F.data == "gpt_finish")
async def gpt_finish(callback: CallbackQuery,state: FSMContext,):
    await callback.answer("GPT завершён")
    await state.clear()

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="start")
        ),
        caption=FileManager.read_txt(
            Path.MESSAGES,
            "start",
        ),
        reply_markup=keyboard_main_menu(),
    )