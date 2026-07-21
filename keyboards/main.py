from aiogram.utils.keyboard import InlineKeyboardBuilder


def keyboard_main_menu():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="🎲 Random", callback_data="random")
    keyboard.button(text="🤖 GPT", callback_data="gpt")
    keyboard.button(text="💬 Talk", callback_data="talk")
    keyboard.button(text="❓ Quiz", callback_data="quiz")

    keyboard.adjust(2)

    return keyboard.as_markup()