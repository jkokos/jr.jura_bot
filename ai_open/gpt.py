import openai
from aiogram import Bot
#import httpx
import config
from .enums import GPTModel
from .gpt_message import GPTMessage


class GPTService:
    _instance = None  # sozdaem objekt dlja obrachenija k GPT


    def __new__(cls,*args,**kwargs):   # realizacija obrashenija
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self,model:GPTModel = GPTModel.GPT_5_5): # inicializator
        self._gpt_token = config.OPEAI_API_KEY
        #self._proxy = config.PROXY
        self._client = self._create_client()
        self._model = model.value

    def _create_client(self):                      #sozdanie clienta
        gpt_client = openai.AsyncOpenAI(
            apy_key=self._gpt_token,
            #http_client=httpx.AsyncClient(
                #proxy=self._proxy,
            #)
        )
        return gpt_client


    async def request(self,message_list: GPTMessage, bot:Bot):   #otpravka oshibki adminu
        try:
            response = await self._client.chat.completions.create(
                message=message_list.message_list,
                model=self.model
            )
            return response.choices[0].message.content
        except Exception as e:
            await bot.send_message(
                chat_id=config.ADMIN_ID,
                text=str(e),
            )

    async def transcript_voice(self,file,bot:Bot):
        try:
            with open(file,"rb")as audio_file:
                transcript = await self._client.audio.transcriptions.create(
                    model=GPTModel.WHISPER.value,
                    file=audio_file
                )
                return transcript.text
        except Exception as e:
            await bot.send_message(
                chat_id=config.ADMIN_ID,
                text=str(e),
            )
















