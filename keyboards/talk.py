from aiogram.utils.keyboard import InlineKeyboardBuilder

def keyboard_stars():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="В.И. Ленин",
        callback_data="star_lenin"
    )
    builder.button(
        text="Илон Маск",
        callback_data="star_elon"
    )
    builder.button(
        text="Курт Кобейн",
        callback_data="star_kurt"
    )
    builder.button(
        text="❌ Отмена",
        callback_data="talk_finish"
    )

    builder.adjust(1)

    return builder.as_markup()


def keyboard_talk():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="⭐ Сменить знаменитость",
        callback_data="change_star"
    )
    builder.button(
        text="❌ Завершить",
        callback_data="talk_finish"
    )

    builder.adjust(1)

    return builder.as_markup()