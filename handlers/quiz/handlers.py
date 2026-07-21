
from handlers.quiz.states import QuizState
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types.input_file import FSInputFile

from keyboards import (
    keyboard_main_menu,
    keyboard_quiz,
    keyboard_quiz_topics,

)
from utils import FileManager
from utils.enum_path import Path
from handlers.quiz.data import QUIZ_TOPICS
from .utils import (
    normalize_quiz_answer,
    quiz_answers_are_equal,
    parse_quiz_response,
    generate_quiz_question,
)
import logging

logger = logging.getLogger(__name__)

quiz_router = Router()

@quiz_router.callback_query(F.data == "quiz")
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

@quiz_router.callback_query(QuizState.choosing_topic,F.data.in_(QUIZ_TOPICS.keys()),)
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

@quiz_router.message(QuizState.waiting_answer)
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

@quiz_router.callback_query(QuizState.waiting_answer,F.data == "quiz_more",)
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

@quiz_router.callback_query(F.data == "quiz_finish")
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
