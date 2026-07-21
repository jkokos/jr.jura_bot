from aiogram import Bot,F,Router
from aiogram.types import CallbackQuery
from aiogram.types.input_file import FSInputFile

from ai_open import chat_gpt
from ai_open.gpt_messages import GPTMessage

from keyboards import ikb_random, keyboard_main_menu

from utils import FileManager
from utils.enum_path import  Path

random_router = Router()

@random_router.callback_query(F.data == "random")
async def random_button(callback: CallbackQuery,bot: Bot,):
    await callback.answer()

    response = await chat_gpt.request(GPTMessage("random"),bot,)

    await callback.message.answer_photo(photo=FSInputFile(Path.IMAGES.value.format(file="random")
        ),
        caption=response,
        reply_markup=ikb_random(),
    )


@random_router.callback_query(F.data == "random_more")
async def more_random(callback: CallbackQuery,bot: Bot,):
    await callback.answer()

    response = await chat_gpt.request(GPTMessage("random"),bot,)

    await callback.message.edit_caption(caption=response,reply_markup=ikb_random(),)


@random_router.callback_query(F.data == "random_finish")
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