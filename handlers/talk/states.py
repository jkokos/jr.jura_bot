from aiogram.fsm.state import State, StatesGroup


class TalkState(StatesGroup):
    choosing_star = State()
    waiting_message = State()