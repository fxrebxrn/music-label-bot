from aiogram.fsm.state import State, StatesGroup

class AccountLinkStates(StatesGroup):
    artist_nickname = State()
    topic_channel_link = State()
    main_channel_link = State()
    topic_videos_links = State()
    main_videos_links = State()
    preview = State()
