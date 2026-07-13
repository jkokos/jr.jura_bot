import dotenv
import os
from aiogram import Bot,Dispatcher




dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN") #beret token
ADMIN_ID = int(os.getenv('ADMIN_ID')) # beret adminku
OPENAI_API_TOKEN = os.getenv('OPEN_API_KEY')
# print(TOKEN)
# print(type(TOKEN))