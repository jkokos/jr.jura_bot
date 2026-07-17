
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards import (
    keyboard_main_menu,
    ikb_random,
    keyboard_gpt,
    keyboard_talk,
    keyboard_stars,
    keyboard_quiz,
    keyboard_quiz_topics
)

import config

from utils import FileManager
from utils.enum_path import Path
from ai_open import chat_gpt
from ai_open.gpt_messages import GPTMessage
import logging

main_router = Router()

logger = logging.getLogger(__name__)



class GPTState(StatesGroup):
    waiting_question = State()


class TalkState(StatesGroup):
    choosing_star = State()
    waiting_message = State()

class QuizState(StatesGroup):
    choosing_topic = State()
    waiting_answer = State()


STARS = {
    "star_lenin": {
        "name": "В.И. Ленин",
        "prompt": "talk_lenin",
    },

    "star_elon": {
        "name": "Илон Маск",
        "prompt": "talk_elon",
    },

    "star_kurt": {
        "name": "Курт Кобейн",
        "prompt": "talk_cobain",
    },
}


QUIZ_TOPICS = {
    "quiz_prog": "🐍 Python",
    "quiz_math": "📐 Математика",
    "quiz_biology": "🧬 Биология",
}


@main_router.message(Command("start")) # START

async def command_handler(
    message: Message,
    state: FSMContext
):
    await state.clear()

    await message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="start")
        ),
        caption=FileManager.read_txt(
            Path.MESSAGES,
            "start"
        ),
        reply_markup=keyboard_main_menu()
    )

@main_router.callback_query(F.data == "random") # RANDOM
async def random_button(callback: CallbackQuery,bot: Bot):
    await callback.answer()

    response = await chat_gpt.request(GPTMessage("random"),bot)

    await callback.message.answer_photo(
        photo=FSInputFile(
            Path.IMAGES.value.format(file="random")
        ),
        caption=response,
        reply_markup=ikb_random()
    )

@main_router.callback_query(F.data == "more")
async def more_random(callback: CallbackQuery,bot: Bot):
    await callback.answer()

    response = await chat_gpt.request(GPTMessage("random"),bot)

    await callback.message.edit_caption(caption=response,reply_markup=ikb_random())


@main_router.callback_query(F.data == "finish")
async def finish_random(callback: CallbackQuery,state: FSMContext):
    await callback.answer("Завершено")
    await state.clear()

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer_photo(
        photo=FSInputFile(
            Path.IMAGES.value.format(file="start")
        ),
        caption=FileManager.read_txt(
            Path.MESSAGES,
            "start"
        ),
        reply_markup=keyboard_main_menu()
    )


@main_router.callback_query(F.data == "gpt") # GPT
async def gpt_button(callback: CallbackQuery,state: FSMContext):
    await callback.answer()

    await state.set_state(GPTState.waiting_question)

    await callback.message.answer_photo(
        photo=FSInputFile(
            Path.IMAGES.value.format(file="gpt")
        ),
        caption="Напишите вопрос для GPT:",
        reply_markup=keyboard_gpt()
    )


@main_router.message(Command("gpt"))
async def gpt_command(message: Message,state: FSMContext):
    await state.set_state(GPTState.waiting_question)

    await message.answer_photo(
        photo=FSInputFile(
            Path.IMAGES.value.format(file="gpt")
        ),
        caption="Напишите вопрос для GPT:",
        reply_markup=keyboard_gpt()
    )


@main_router.message(GPTState.waiting_question)
async def gpt_answer(message: Message,bot: Bot):
    if not message.text:
        await message.answer("Задай вопрос.")
        return

    await message.answer("Думаю...")

    gpt_message = GPTMessage("gpt")

    gpt_message.message_list.append({
        "role": "user",
        "content": message.text,
    })

    response = await chat_gpt.request(gpt_message,bot)

    await message.answer(response,reply_markup=keyboard_gpt())


@main_router.callback_query(F.data == "gpt_finish")
async def gpt_finish(callback: CallbackQuery,state: FSMContext):
    await callback.answer("GPT Сompleted ")

    await state.clear()

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer_photo(
        photo=FSInputFile(
            Path.IMAGES.value.format(file="start")
        ),
        caption=FileManager.read_txt(
            Path.MESSAGES,
            "start"
        ),
        reply_markup=keyboard_main_menu()
    )

@main_router.callback_query(F.data == "talk") # TALK
async def talk_button(callback: CallbackQuery,state: FSMContext):
    await callback.answer()

    await state.set_state(TalkState.choosing_star)

    await callback.message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="talk")
        ),
        caption="Выбери знаменитость:",
        reply_markup=keyboard_stars()
    )


@main_router.message(Command("talk"))
async def talk_command(message: Message,state: FSMContext):
    await state.set_state(
        TalkState.choosing_star
    )

    await message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="talk")
        ),
        caption="Выбери знаменитость:",
        reply_markup=keyboard_stars()
    )


@main_router.callback_query(TalkState.choosing_star,F.data.in_(STARS.keys()))
async def choose_star(callback: CallbackQuery,state: FSMContext):
    star = STARS.get(callback.data)

    if not star:
        await callback.answer(
            "Нет такого",
            show_alert=True
        )
        return

    await state.update_data(
        star_name=star["name"],
        prompt_name=star["prompt"]
    )

    await state.set_state(
        TalkState.waiting_message
    )

    await callback.answer(
        f"Ты выбрал: {star['name']}"
    )

    await callback.message.edit_caption(
        caption=(
            f"Ты выбрал: {star['name']}\n\n"
            "напиши сообщение."
        ),
        reply_markup=keyboard_talk()
    )


@main_router.message(TalkState.waiting_message)
async def talk_answer(message: Message,state: FSMContext,bot: Bot):
    if not message.text:
        await message.answer(
            "Отправь сообщение."
        )
        return

    data = await state.get_data()

    star_name = data.get("star_name")
    prompt_name = data.get("prompt_name")

    if not prompt_name:
        await state.set_state(TalkState.choosing_star)

        await message.answer(
            "Сначала выбери знаменитость:",
            reply_markup=keyboard_stars()
        )
        return

    await message.answer(
        f"{star_name} думает..."
    )

    gpt_message = GPTMessage(prompt_name)

    gpt_message.message_list.append({
        "role": "user",
        "content": message.text,
    })

    response = await chat_gpt.request(
        gpt_message,
        bot
    )

    await message.answer(
        response,
        reply_markup=keyboard_talk()
    )


@main_router.callback_query(F.data == "change_star")
async def change_star(callback: CallbackQuery,state: FSMContext):
    await callback.answer()

    await state.set_state(TalkState.choosing_star)

    await callback.message.answer(
        "Выбери другую знаменитость:",
        reply_markup=keyboard_stars()
    )


@main_router.callback_query(F.data == "talk_finish")
async def talk_finish(callback: CallbackQuery,state: FSMContext):
    await callback.answer(
        "Диалог завершён"
    )

    await state.clear()

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer_photo(
        photo=FSInputFile(
            Path.IMAGES.value.format(file="start")
        ),
        caption=FileManager.read_txt(
            Path.MESSAGES,
            "start"
        ),
        reply_markup=keyboard_main_menu()
    )

@main_router.callback_query(F.data == "quiz")
async def quiz_button(callback: CallbackQuery,state: FSMContext):
    await callback.answer()


    await state.clear()


    await state.set_state(QuizState.choosing_topic)

    await callback.message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="quiz")
        ),
        caption=(
            "Викторина\n\n"
            "Выберите тему:"
        ),
        reply_markup=keyboard_quiz_topics()
    )


@main_router.callback_query(QuizState.choosing_topic,F.data.in_(QUIZ_TOPICS.keys()))
async def quiz_choose_topic(callback: CallbackQuery,state: FSMContext,bot: Bot):
    topic_command = callback.data
    topic_name = QUIZ_TOPICS[topic_command]


    quiz_message = GPTMessage("quiz")


    quiz_message.message_list.append({
        "role": "user",
        "content": topic_command
    })

    await callback.answer(
        f"Выбрана тема: {topic_name}"
    )

    await callback.message.edit_caption(
        caption=(
            f"{topic_name}\n\n"
            "Генерирую вопрос..."
        ),
        reply_markup=None
    )


    question = await chat_gpt.request(
        quiz_message,
        bot
    )


    await state.update_data(
        quiz_messages=quiz_message.message_list,
        quiz_topic=topic_command,
        quiz_topic_name=topic_name
    )


    await state.set_state(
        QuizState.waiting_answer
    )

    await callback.message.edit_caption(
        caption=(
            f"{topic_name}\n\n"
            f"{question}"
        ),
        reply_markup=keyboard_quiz()
    )


@main_router.message(QuizState.waiting_answer)
async def quiz_check_answer(message: Message,state: FSMContext,bot: Bot):
    if not message.text:
        await message.answer(
            "Напиши ответ текстом."
        )
        return

    data = await state.get_data()

    quiz_messages = data.get("quiz_messages")

    if not quiz_messages:
        await message.answer(
            "Сессия викторины потеряна. "
            "Запусти Quiz заново."
        )
        await state.clear()
        return


    quiz_message = GPTMessage("quiz")


    quiz_message.message_list = quiz_messages


    quiz_message.message_list.append({
        "role": "user",
        "content": message.text
    })

    await message.answer("Проверяю ответ...")


    result = await chat_gpt.request(
        quiz_message,
        bot
    )


    await state.update_data(
        quiz_messages=quiz_message.message_list
    )

    await message.answer(
        result,
        reply_markup=keyboard_quiz()
    )


@main_router.callback_query(QuizState.waiting_answer,F.data == "quiz_more")
async def quiz_more(callback: CallbackQuery,state: FSMContext,bot: Bot):
    data = await state.get_data()

    quiz_messages = data.get("quiz_messages")
    topic_name = data.get(
        "quiz_topic_name",
        "Викторина"
    )

    if not quiz_messages:
        await callback.answer(
            "Сессия викторины потеряна",
            show_alert=True
        )
        await state.clear()
        return

    await callback.answer()


    quiz_message = GPTMessage("quiz")
    quiz_message.message_list = quiz_messages


    quiz_message.message_list.append({
        "role": "user",
        "content": "quiz_more"
    })

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    waiting_message = await callback.message.answer(
        "Генерирую следующий вопрос..."
    )

    question = await chat_gpt.request(
        quiz_message,
        bot
    )


    await state.update_data(
        quiz_messages=quiz_message.message_list
    )


    await waiting_message.delete()

    await callback.message.answer(
        text=(
            f"{topic_name}\n\n"
            f"{question}"
        ),
        reply_markup=keyboard_quiz()
    )


@main_router.callback_query(F.data == "quiz_finish")
async def quiz_finish(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer(
        "Викторина завершена"
    )

    await state.clear()


    await callback.message.edit_reply_markup(
        reply_markup=None
    )


    await callback.message.answer_photo(
        photo=FSInputFile(
            Path.IMAGES.value.format(file="start")
        ),
        caption=FileManager.read_txt(
            Path.MESSAGES,
            "start"
        ),
        reply_markup=keyboard_main_menu()
    )

@main_router.message()
async def all_messages(message: Message,bot: Bot):
    msg_text = (
        f"Пользователь: "
        f"{message.from_user.full_name} написал:\n"
        f"{message.text or 'Сообщение без текста'}"
    )

    await bot.send_message(chat_id=config.ADMIN_ID,text=msg_text)