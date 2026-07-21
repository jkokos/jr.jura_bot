from aiogram.utils.keyboard import InlineKeyboardBuilder

def keyboard_quiz():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="More",
        callback_data="quiz_more"
    )

    builder.button(
        text="Finish",
        callback_data="quiz_finish"
    )

    builder.adjust(2)

    return builder.as_markup()


def keyboard_quiz_topics():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🐍 Python",
        callback_data="quiz_prog"
    )

    builder.button(
        text="📐 Математика",
        callback_data="quiz_math"
    )

    builder.button(
        text="🧬 Биология",
        callback_data="quiz_biology"
    )

    builder.button(
        text="Finish",
        callback_data="quiz_finish"
    )

    builder.adjust(1)

    return builder.as_markup()