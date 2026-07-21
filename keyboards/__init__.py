from .main import keyboard_main_menu
from .random import ikb_random
from .gpt import keyboard_gpt
from .talk import keyboard_stars, keyboard_talk
from .quiz import (
    keyboard_quiz,
    keyboard_quiz_topics,
)

__all__ = [
    "keyboard_main_menu",
    "ikb_random",
    "keyboard_gpt",
    "keyboard_stars",
    "keyboard_talk",
    "keyboard_quiz",
    "keyboard_quiz_topics",
]








# from aiogram.utils.keyboard import InlineKeyboardBuilder
#
#
# def keyboard_main_menu():
#     keyboard = InlineKeyboardBuilder()
#
#     keyboard.button(text="🎲 Random", callback_data="random")
#     keyboard.button(text="🤖 GPT", callback_data="gpt")
#     keyboard.button(text="💬 Talk", callback_data="talk")
#     keyboard.button(text="❓ Quiz", callback_data="quiz")
#
#     keyboard.adjust(2)
#
#     return keyboard.as_markup()


# def ikb_random():
#     keyboard = InlineKeyboardBuilder()
#
#     keyboard.button(text="More", callback_data="more")
#     keyboard.button(text="Finish", callback_data="finish")
#
#     keyboard.adjust(2)
#
#     return keyboard.as_markup()



# def keyboard_gpt():
#     keyboard = InlineKeyboardBuilder()
#     keyboard.button(
#         text="Finish",
#         callback_data="gpt_finish"
#     )
#     return keyboard.as_markup()

# def keyboard_stars():
#     builder = InlineKeyboardBuilder()
#
#     builder.button(
#         text="В.И. Ленин",
#         callback_data="star_lenin"
#     )
#     builder.button(
#         text="Илон Маск",
#         callback_data="star_elon"
#     )
#     builder.button(
#         text="Курт Кобейн",
#         callback_data="star_kurt"
#     )
#     builder.button(
#         text="❌ Отмена",
#         callback_data="talk_finish"
#     )
#
#     builder.adjust(1)
#
#     return builder.as_markup()
#
#
# def keyboard_talk():
#     builder = InlineKeyboardBuilder()
#
#     builder.button(
#         text="⭐ Сменить знаменитость",
#         callback_data="change_star"
#     )
#     builder.button(
#         text="❌ Завершить",
#         callback_data="talk_finish"
#     )
#
#     builder.adjust(1)
#
#     return builder.as_markup()


# def keyboard_quiz():
#     builder = InlineKeyboardBuilder()
#
#     builder.button(
#         text="More",
#         callback_data="quiz_more"
#     )
#
#     builder.button(
#         text="Finish",
#         callback_data="quiz_finish"
#     )
#
#     builder.adjust(2)
#
#     return builder.as_markup()
#
#
# def keyboard_quiz_topics():
#     builder = InlineKeyboardBuilder()
#
#     builder.button(
#         text="🐍 Python",
#         callback_data="quiz_prog"
#     )
#
#     builder.button(
#         text="📐 Математика",
#         callback_data="quiz_math"
#     )
#
#     builder.button(
#         text="🧬 Биология",
#         callback_data="quiz_biology"
#     )
#
#     builder.button(
#         text="Finish",
#         callback_data="quiz_finish"
#     )
#
#     builder.adjust(1)
#
#     return builder.as_markup()


