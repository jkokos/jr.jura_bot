from aiogram.utils.keyboard import InlineKeyboardBuilder

def keyboard_gpt():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="Finish",
        callback_data="gpt_finish"
    )
    return keyboard.as_markup()