from aiogram.fsm.state import State, StatesGroup


class Violation(StatesGroup):
    s1 = State()
    s2 = State()
    s3 = State()
    s4 = State()
    s5 = State()
    s6 = State()


class Admin(StatesGroup):
    add_claim = State()
    search_claim = State()
    send_message = State()
    send_message_msg = State()
