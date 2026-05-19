from aiogram.fsm.state import State, StatesGroup


class ReleaseStates(StatesGroup):
    distribution_type = State()
    artist_type = State()
    release_format = State()
    main_artists = State()
    release_title = State()
    tracks_order = State()
    explicit_content = State()
    release_date = State()
    genre = State()
    materials_link = State()
    artist_full_name = State()
    comment = State()
    preview = State()
