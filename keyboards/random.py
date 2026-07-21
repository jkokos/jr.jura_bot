from aiogram.utils.keyboard import InlineKeyboardBuilder


def ikb_random():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="More", callback_data="random_more")
    keyboard.button(text="Finish", callback_data="random_finish")
    keyboard.adjust(2)

    return keyboard.as_markup()