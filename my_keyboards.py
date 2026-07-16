from aiogram.utils.keyboard import InlineKeyboardBuilder


#создание клавиатуры

def keyboard_main_menu():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="🎲 Random", callback_data="random")

    keyboard.button(text="🤖 GPT", callback_data="gpt")

    keyboard.button(text="💬 Talk", callback_data="talk")

    keyboard.button(text="❓ Quiz", callback_data="quiz")

    keyboard.adjust(2)
    return keyboard.as_markup()




def ikb_random():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="More",
        callback_data="more",
    )

    keyboard.button(
        text="Finish",
    callback_data="finish",
    )

    keyboard.adjust(2)
    return keyboard.as_markup()


def keyboard_gpt():
    keyboard = InlineKeyboardBuilder

    keyboard.button(
        text = "Finish",
        callback_data = "finish",
    )
    return keyboard.as_markup
