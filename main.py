from aiogram import Bot, Dispatcher
import asyncio
from dotenv import load_dotenv
from handlers import main_router
import config
import misc
import logging
from logger_config import setup_logging



load_dotenv()

setup_logging()
logger = logging.getLogger(__name__)


bot = Bot(token=config.TOKEN)
dp = Dispatcher()



async def start_bot():
    dp.startup.register(misc.on_start) # иконка в начале
    dp.shutdown.register(misc.on_shutdown) # иконка в конце
    dp.include_router(main_router) # запуск роутера в хандлер
    logger.info("Поехали")
    try:
        await dp.start_polling(bot) # запускаем бесконечный цикл
    except Exception:
        logger.exception("Что то пошло не так")
        raise
    finally:
        logger.info("close")

# print('work')
if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt: # падает без ошибок
        pass
