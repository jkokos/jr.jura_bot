from aiogram import Bot,Dispatcher
import asyncio
from dotenv import load_dotenv
import config
load_dotenv()

bot = Bot(token=config.TOKEN)
dp = Dispatcher()







async def start_bot():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(start_bot())




