from aiogram import Router

from .start import start_router
from .random import random_router
from .gpt import gpt_router
from .talk import talk_router
from .quiz import quiz_router
from .admin import admin_router

main_router = Router()

main_router.include_router(start_router)
main_router.include_router(random_router)
main_router.include_router(gpt_router)
main_router.include_router(talk_router)
main_router.include_router(quiz_router)

# Должен быть последним!
main_router.include_router(admin_router)