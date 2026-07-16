from enum import Enum


class GPTRole(Enum):
    USER = 'user'
    CHAT = 'assistant'
    SYSTEM ='system'


class GPTModel(Enum):
    GPT_5_4_nano = 'gpt-5.4-nano'
    GPT_5_nano = 'gpt-5-nano'

    GPT_5_4_mini = 'gpt-5.4-mini'
    GPT_5_mini = 'gpt-5-mini'
    WHISPER = 'whisper-1'
    GPT_IMAGE = 'dall-e-3'