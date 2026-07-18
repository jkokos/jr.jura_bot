import json
import logging
import re
import unicodedata
from difflib import SequenceMatcher

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.types.input_file import FSInputFile

import config
from ai_open import chat_gpt
from ai_open.gpt_messages import GPTMessage
from keyboards import (
    ikb_random,
    keyboard_gpt,
    keyboard_main_menu,
    keyboard_quiz,
    keyboard_quiz_topics,
    keyboard_stars,
    keyboard_talk,
)
from utils import FileManager
from utils.enum_path import Path


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




def normalize_quiz_answer(text: str) -> str: #Подготавливает ответ для сравнения.


    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.lower().strip()


    text = re.sub(r"[«»\"'`(){}\[\].,!?;:]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()

       #Сравнивает ответ пользователя с допустимыми ответами.
def quiz_answers_are_equal(user_answer: str,accepted_answers: list[str],) -> bool:


    normalized_user = normalize_quiz_answer(user_answer)

    if not normalized_user:
        return False

    for accepted_answer in accepted_answers:
        normalized_correct = normalize_quiz_answer(accepted_answer)

        if not normalized_correct:
            continue


        if normalized_user == normalized_correct:    # Точное совпадение
            return True

        # Небольшая опечатка
        similarity = SequenceMatcher(
            None,
            normalized_user,
            normalized_correct,
        ).ratio()

        # Для очень коротких ответов нужна почти полная точность
        threshold = 0.95 if len(normalized_correct) <= 4 else 0.88

        if similarity >= threshold:
            return True

    return False


def parse_quiz_response(response: str) -> dict: #Извлекает и проверяет JSON, который вернул GPT


    if not response:
        raise ValueError("GPT вернул пустой ответ")

    clean_response = response.strip()


    clean_response = re.sub(
        r"^```(?:json)?\s*",
        "",
        clean_response,
        flags=re.IGNORECASE,
    )
    clean_response = re.sub(r"\s*```$", "", clean_response)

    json_match = re.search(
        r"\{.*\}",
        clean_response,
        flags=re.DOTALL,
    )

    if not json_match:
        raise ValueError("В ответе GPT не найден JSON")

    quiz_data = json.loads(json_match.group())

    question = quiz_data.get("question")
    correct_answer = quiz_data.get("correct_answer")
    accepted_answers = quiz_data.get("accepted_answers", [])
    explanation = quiz_data.get("explanation", "")

    if not isinstance(question, str) or not question.strip():
        raise ValueError("GPT не вернул вопрос")

    if not isinstance(correct_answer, str) or not correct_answer.strip():
        raise ValueError("GPT не вернул правильный ответ")

    if not isinstance(accepted_answers, list):
        accepted_answers = []

    # Основной ответ всегда добавляется в список допустимых
    all_answers = [correct_answer, *accepted_answers]
    unique_answers: list[str] = []
    normalized_seen: set[str] = set()

    for answer in all_answers:
        if not isinstance(answer, str):
            continue

        answer = answer.strip()
        normalized = normalize_quiz_answer(answer)

        if not normalized or normalized in normalized_seen:
            continue

        normalized_seen.add(normalized)
        unique_answers.append(answer)

    return {
        "question": question.strip(),
        "correct_answer": correct_answer.strip(),
        "accepted_answers": unique_answers,
        "explanation": (
            explanation.strip()
            if isinstance(explanation, str)
            else ""
        ),
    }


async def generate_quiz_question(bot: Bot,topic_command: str,topic_name: str,used_questions: list[str] | None = None,) -> dict:
    #Создаёт новый вопрос через GPT и возвращает данные вопроса

    used_questions = used_questions or []

    previous_questions = "\n".join(
        f"- {question}"
        for question in used_questions[-15:]
    )

    if not previous_questions:
        previous_questions = "Предыдущих вопросов нет."

    quiz_message = GPTMessage("quiz")

    quiz_message.message_list.append({
        "role": "user",
        "content": (
            "Создай один новый вопрос для викторины.\n\n"
            f"Команда темы: {topic_command}\n"
            f"Название темы: {topic_name}\n\n"
            "Требования:\n"
            "1. Создай только один вопрос.\n"
            "2. Правильный ответ должен состоять максимум из нескольких слов.\n"
            "3. Не создавай вопрос с числовым ответом.\n"
            "4. Вопрос должен иметь один однозначный правильный ответ.\n"
            "5. Не повторяй предыдущие вопросы.\n"
            "6. В accepted_answers укажи только правильные варианты написания.\n"
            "7. Не добавляй близкие по теме, но неправильные ответы.\n\n"
            "Предыдущие вопросы:\n"
            f"{previous_questions}\n\n"
            "Верни только корректный JSON без Markdown:\n"
            "{\n"
            '  "question": "Текст вопроса",\n'
            '  "correct_answer": "Основной правильный ответ",\n'
            '  "accepted_answers": ["вариант 1", "вариант 2"],\n'
            '  "explanation": "Короткое объяснение"\n'
            "}"
        ),
    })

    response = await chat_gpt.request(quiz_message, bot)
    return parse_quiz_response(response)




@main_router.message(Command("start"))
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




@main_router.callback_query(F.data == "random")
async def random_button(callback: CallbackQuery,bot: Bot,):
    await callback.answer()

    response = await chat_gpt.request(GPTMessage("random"),bot,)

    await callback.message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="random")
        ),
        caption=response,
        reply_markup=ikb_random(),
    )


@main_router.callback_query(F.data == "more")
async def more_random(callback: CallbackQuery,bot: Bot,):
    await callback.answer()

    response = await chat_gpt.request(GPTMessage("random"),bot,)

    await callback.message.edit_caption(caption=response,reply_markup=ikb_random(),)


@main_router.callback_query(F.data == "finish")
async def finish_random(callback: CallbackQuery,state: FSMContext,):
    await callback.answer("Завершено")
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




@main_router.callback_query(F.data == "gpt")
async def gpt_button(callback: CallbackQuery,state: FSMContext,):
    await callback.answer()
    await state.set_state(GPTState.waiting_question)

    await callback.message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="gpt")
        ),
        caption="Напишите вопрос для GPT:",
        reply_markup=keyboard_gpt(),
    )


@main_router.message(Command("gpt"))
async def gpt_command(message: Message,state: FSMContext,):
    await state.set_state(GPTState.waiting_question)

    await message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="gpt")
        ),
        caption="Напишите вопрос для GPT:",
        reply_markup=keyboard_gpt(),
    )


@main_router.message(GPTState.waiting_question)
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


@main_router.callback_query(F.data == "gpt_finish")
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




@main_router.callback_query(F.data == "talk")
async def talk_button(callback: CallbackQuery,state: FSMContext,):
    await callback.answer()
    await state.set_state(TalkState.choosing_star)

    await callback.message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="talk")
        ),
        caption="Выбери знаменитость:",
        reply_markup=keyboard_stars(),
    )


@main_router.message(Command("talk"))
async def talk_command(message: Message,state: FSMContext,):
    await state.set_state(TalkState.choosing_star)

    await message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="talk")
        ),
        caption="Выбери знаменитость:",
        reply_markup=keyboard_stars(),
    )


@main_router.callback_query(TalkState.choosing_star,F.data.in_(STARS.keys()),)
async def choose_star(callback: CallbackQuery,state: FSMContext,):
    star = STARS.get(callback.data)

    if not star:
        await callback.answer("Нет такой знаменитости",show_alert=True,)
        return

    await state.update_data(star_name=star["name"],prompt_name=star["prompt"],)

    await state.set_state(TalkState.waiting_message)

    await callback.answer(f"Ты выбрал: {star['name']}")

    await callback.message.edit_caption(caption=(f"Ты выбрал: {star['name']}\n\n""Напиши сообщение."),reply_markup=keyboard_talk(),)


@main_router.message(TalkState.waiting_message)
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

    response = await chat_gpt.request(
        gpt_message,
        bot,
    )

    await message.answer(
        response,
        reply_markup=keyboard_talk(),
    )


@main_router.callback_query(F.data == "change_star")
async def change_star(callback: CallbackQuery,state: FSMContext,):
    await callback.answer()
    await state.set_state(TalkState.choosing_star)

    await callback.message.answer("Выбери другую знаменитость:",reply_markup=keyboard_stars(),)


@main_router.callback_query(F.data == "talk_finish")
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




@main_router.callback_query(F.data == "quiz")
async def quiz_button(callback: CallbackQuery,state: FSMContext,):
    await callback.answer()
    await state.clear()
    await state.set_state(QuizState.choosing_topic)

    await callback.message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="quiz")
        ),
        caption=(
            "Викторина\n\n"
            "Выбери тему:"
        ),
        reply_markup=keyboard_quiz_topics(),
    )




@main_router.callback_query(QuizState.choosing_topic,F.data.in_(QUIZ_TOPICS.keys()),)
async def quiz_choose_topic(callback: CallbackQuery,state: FSMContext,bot: Bot,):
    topic_command = callback.data
    topic_name = QUIZ_TOPICS.get(topic_command)

    if not topic_name:
        await callback.answer("Такой темы нет",show_alert=True,)
        return

    await callback.answer(f"Выбрана тема: {topic_name}")

    await callback.message.edit_caption(caption=(f"{topic_name}\n\n""Генерирую первый вопрос..."),reply_markup=None,)

    try:
        quiz_data = await generate_quiz_question(bot=bot,topic_command=topic_command,topic_name=topic_name,used_questions=[],)
    except Exception as error:
        logger.exception(
            "Ошибка генерации первого вопроса: %s",
            error,
        )

        await callback.message.edit_caption(
            caption=(
                "Не удалось создать вопрос.\n\n"
                "Выбери тему ещё раз."
            ),
            reply_markup=keyboard_quiz_topics(),
        )

        await state.set_state(QuizState.choosing_topic)
        return

    question = quiz_data["question"]

    await state.update_data(
        quiz_topic=topic_command,
        quiz_topic_name=topic_name,
        current_question=question,
        correct_answer=quiz_data["correct_answer"],
        accepted_answers=quiz_data["accepted_answers"],
        explanation=quiz_data["explanation"],
        correct=0,
        wrong=0,
        answered=False,
        generating=False,
        used_questions=[question],
    )

    await state.set_state(QuizState.waiting_answer)

    await callback.message.edit_caption(
        caption=(
            f"{topic_name}\n\n"
            f"{question}\n\n"
            "Текущий счёт:\n"
            " 0  |   0"
        ),
        reply_markup=keyboard_quiz(),
    )




@main_router.message(QuizState.waiting_answer)
async def quiz_check_answer(message: Message,state: FSMContext,):
    if not message.text:
        await message.answer("Напиши ответ текстом.")
        return

    data = await state.get_data()

    current_question = data.get("current_question")
    correct_answer = data.get("correct_answer")
    accepted_answers = data.get("accepted_answers", [])
    explanation = data.get("explanation", "")
    correct = data.get("correct", 0)
    wrong = data.get("wrong", 0)
    answered = data.get("answered", False)
    generating = data.get("generating", False)

    if generating:
        await message.answer("Подожди, создаётся следующий вопрос.")
        return

    if (
        not current_question
        or not correct_answer
        or not accepted_answers
    ):
        await message.answer(
            "Сессия викторины потеряна.\n"
            "Запусти Quiz заново."
        )
        await state.clear()
        return

    if answered:
        await message.answer(
            "Ты уже ответил на этот вопрос.\n\n"
            "Нажми More для следующего вопроса.",
            reply_markup=keyboard_quiz(),
        )
        return

    answer_is_correct = quiz_answers_are_equal(
        user_answer=message.text,
        accepted_answers=accepted_answers,
    )

    if answer_is_correct:
        correct += 1
        result_text = "Правильно!"

        if explanation:
            result_text += f"\n\n💡 {explanation}"
    else:
        wrong += 1
        result_text = (
            "Неправильно!\n\n"
            f"Правильный ответ: {correct_answer}"
        )

        if explanation:
            result_text += f"\n\n💡 {explanation}"

    await state.update_data(
        correct=correct,
        wrong=wrong,
        answered=True,
    )

    await message.answer(
        text=(
            f"{result_text}\n\n"
            "Счёт:\n"
            f"Правильных: {correct}\n"
            f"Неправильных: {wrong}\n\n"
            "Нажми More для следующего вопроса."
        ),
        reply_markup=keyboard_quiz(),
    )




@main_router.callback_query(QuizState.waiting_answer,F.data == "quiz_more",)
async def quiz_more(callback: CallbackQuery,state: FSMContext,bot: Bot,):
    data = await state.get_data()

    if data.get("generating", False):
        await callback.answer("Вопрос уже создаётся",show_alert=False,)
        return

    await callback.answer()

    topic_command = data.get("quiz_topic")
    topic_name = data.get(
        "quiz_topic_name",
        "Викторина",
    )
    correct = data.get("correct", 0)
    wrong = data.get("wrong", 0)
    used_questions = data.get(
        "used_questions",
        [],
    )

    if not topic_command:
        await callback.message.answer(
            "Сессия викторины потеряна.\n"
            "Запусти Quiz заново."
        )
        await state.clear()
        return

    await state.update_data(generating=True)

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    waiting_message = await callback.message.answer("Генерирую следующий вопрос...")

    try:
        quiz_data = await generate_quiz_question(bot=bot,topic_command=topic_command,topic_name=topic_name,used_questions=used_questions,)
    except Exception as error:
        logger.exception("Ошибка генерации следующего вопроса: %s",error,)

        await state.update_data(generating=False)

        await waiting_message.edit_text("Не удалось создать вопрос.\n\n""Нажми More ещё раз.",reply_markup=keyboard_quiz(),)
        return

    question = quiz_data["question"]

    new_used_questions = [*used_questions,question,][-20:]

    await state.update_data(
        current_question=question,
        correct_answer=quiz_data["correct_answer"],
        accepted_answers=quiz_data["accepted_answers"],
        explanation=quiz_data["explanation"],
        answered=False,
        generating=False,
        used_questions=new_used_questions,
    )

    try:
        await waiting_message.delete()
    except Exception:
        pass

    await callback.message.answer(
        text=(
            f"{topic_name}\n\n"
            f"{question}\n\n"
            "📊 Текущий счёт:\n"
            f"✅ {correct}  |  ❌ {wrong}"
        ),
        reply_markup=keyboard_quiz(),
    )




@main_router.callback_query(F.data == "quiz_finish")
async def quiz_finish(callback: CallbackQuery,state: FSMContext,):
    data = await state.get_data()

    correct = data.get("correct", 0)
    wrong = data.get("wrong", 0)
    total = correct + wrong

    await callback.answer("Викторина завершена")

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await callback.message.answer(
        text=(
            "Викторина окончена!\n\n"
            "Итоговый результат:\n"
            f"Правильных: {correct}\n"
            f"Неправильных: {wrong}\n"
            f"Всего ответов: {total}"
        )
    )

    await state.clear()

    await callback.message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="start")
        ),
        caption=FileManager.read_txt(
            Path.MESSAGES,
            "start",
        ),
        reply_markup=keyboard_main_menu(),
    )




@main_router.message()
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