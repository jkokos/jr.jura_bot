from aiogram.fsm.state import State, StatesGroup

class GPTState(StatesGroup):
    waiting_question = State()
