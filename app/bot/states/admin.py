from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    search_application_id = State()
    enter_username_for_role = State()
    choose_role = State()
