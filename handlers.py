from aiogram import Router, Bot,F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
from keyboards import keyboard_main_menu, ikb_random, keyboard_gpt
import config
from utils import FileManager
from utils.enum_path import Path
from ai_open import chat_gpt
from ai_open.gpt_messages import GPTMessage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


main_router = Router()

class GPTState(StatesGroup):
    waiting_question = State()

@main_router.message(Command("start"))
async def command_handler(message: Message):
    await message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="start")

        ),
        caption=FileManager.read_txt(
            Path.MESSAGES,
            "start"
        ),
        reply_markup=keyboard_main_menu()
    )




@main_router.callback_query(F.data == "random") # Кнопка Random
async def random_button(
    callback: CallbackQuery,
    bot: Bot
):
    await callback.answer()

    response = await chat_gpt.request(GPTMessage("random"),bot)

    await callback.message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="random")
    ),
        caption=response,
        reply_markup=ikb_random()
    )



@main_router.callback_query(F.data == "gpt") # Кнопка GPT
async def gpt_button(callback: CallbackQuery,state: FSMContext):



    await state.set_state(GPTState.waiting_question)

    await callback.message.answer_photo(
        photo=FSInputFile("resources/images/gpt.jpg"),
        caption="Напишите вопрос для GPT:",
        reply_markup=keyboard_gpt()
    )

    await callback.answer()

@main_router.message(GPTState.waiting_question) # Следующее сообщение пользователя после нажатия GPT
async def gpt_answer(message: Message,state: FSMContext,bot: Bot):
    if not message.text:
        await message.answer("Отправьте вопрос текстом.")
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
async def gpt_finish(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer("Режим GPT завершён")

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

@main_router.callback_query(F.data == "more") # Кнопка More
async def more_random(callback: CallbackQuery,bot: Bot):
    await callback.answer()

    response = await chat_gpt.request(GPTMessage("random"),bot)

    await callback.message.edit_caption(caption=response,reply_markup=ikb_random())




@main_router.callback_query(F.data == "finish") # Кнопка Finish
async def finish_random(callback: CallbackQuery):
    await callback.answer("Завершено")

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




@main_router.message() # Все остальные сообщения
async def all_messages(
    message: Message,
    bot: Bot
):
    msg_text = (
        f"Пользователь: "
        f"{message.from_user.full_name} написал:\n"
        f"{message.text}"
    )

    await bot.send_message(
        chat_id=config.ADMIN_ID,
        text=msg_text
    )
