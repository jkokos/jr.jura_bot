from aiogram.fsm.state import State, StatesGroup


class QuizState(StatesGroup):
    choosing_topic = State()
    waiting_answer = State()