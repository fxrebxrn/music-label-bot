from aiogram.fsm.state import State, StatesGroup

class ModerationStates(StatesGroup):
    approve_comment = State()
    reject_comment = State()
