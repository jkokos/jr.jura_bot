import dotenv
import os
from aiogram import Bot,Dispatcher




dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")

print(TOKEN)
print(type(TOKEN))