from aiogram import Bot,F,Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery,Message
from aiogram.types.input_file import FSInputFile

from ai_open import chat_gpt
from ai_open.gpt_messages import GPTMessage
from handlers.talk.data import STARS
from handlers.talk.states import TalkState
from keyboards import (
    keyboard_main_menu,
    keyboard_stars,
    keyboard_talk,
)

from utils import FileManager
from utils.enum_path import Path

talk_router = Router()


@talk_router.callback_query(F.data == "talk")
async def talk_button(callback: CallbackQuery,state: FSMContext,):
    await callback.answer()
    await state.set_state(TalkState.choosing_star)

    await callback.message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="talk")
        ),
        caption="Выбери знаменитость:",
        reply_markup=keyboard_stars(),
    )
@talk_router.message(Command("talk"))
async def talk_command(message: Message,state: FSMContext,):
    await state.set_state(TalkState.choosing_star)

    await message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="talk")
        ),
        caption="Выбери знаменитость:",
        reply_markup=keyboard_stars(),
    )

@talk_router.callback_query(TalkState.choosing_star,F.data.in_(STARS.keys()),)
async def choose_star(callback: CallbackQuery,state: FSMContext,):
    star = STARS.get(callback.data)

    if not star:
        await callback.answer("Нет такой знаменитости",show_alert=True,)
        return

    await state.update_data(star_name=star["name"],prompt_name=star["prompt"],)

    await state.set_state(TalkState.waiting_message)

    await callback.answer(f"Ты выбрал: {star['name']}")

    await callback.message.edit_caption(caption=(f"Ты выбрал: {star['name']}\n\n""Напиши сообщение."),
                                        reply_markup=keyboard_talk(),
        )

@talk_router.message(TalkState.waiting_message)
async def talk_answer(message: Message,state: FSMContext,bot: Bot,):
    if not message.text:
        await message.answer("Отправь сообщение.")
        return

    data = await state.get_data()

    star_name = data.get("star_name")
    prompt_name = data.get("prompt_name")

    if not prompt_name:
        await state.set_state(TalkState.choosing_star)

        await message.answer(
            "Сначала выбери знаменитость:",
            reply_markup=keyboard_stars(),
        )
        return

    await message.answer(f"{star_name} думает...")

    gpt_message = GPTMessage(prompt_name)
    gpt_message.message_list.append({
        "role": "user",
        "content": message.text,
    })

    response = await chat_gpt.request(gpt_message,bot,)

    await message.answer(response,reply_markup=keyboard_talk(),)

@talk_router.callback_query(F.data == "change_star")
async def change_star(callback: CallbackQuery,state: FSMContext,):
    await callback.answer()
    await state.set_state(TalkState.choosing_star)

    await callback.message.answer("Выбери другую знаменитость:",reply_markup=keyboard_stars(),)


@talk_router.callback_query(F.data == "talk_finish")
async def talk_finish(callback: CallbackQuery,state: FSMContext,):
    await callback.answer("Диалог завершён")
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