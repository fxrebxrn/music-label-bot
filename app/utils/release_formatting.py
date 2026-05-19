from html import escape

from app.db.enums import ArtistType, DistributionType, ReleaseFormat


DISTRIBUTION_TITLES = {
    DistributionType.PAID.value: "Платная",
    DistributionType.FREE.value: "Бесплатная",
}

ARTIST_TYPE_TITLES = {
    ArtistType.SINGER.value: "Исполнитель / Певец",
    ArtistType.PRODUCER.value: "Битмейкер / DJ / Продюсер",
}

RELEASE_FORMAT_TITLES = {
    ReleaseFormat.SINGLE.value: "Сингл",
    ReleaseFormat.EP.value: "EP",
    ReleaseFormat.ALBUM.value: "Альбом",
}


def format_distribution_type(value: str | None) -> str:
    return DISTRIBUTION_TITLES.get(value, value or "-")


def format_artist_type(value: str | None) -> str:
    return ARTIST_TYPE_TITLES.get(value, value or "-")


def format_release_format(value: str | None) -> str:
    return RELEASE_FORMAT_TITLES.get(value, value or "-")


def format_explicit(value: bool | None) -> str:
    return "Да" if value else "Нет"


def get_release_title_from_answers(answers: dict) -> str:
    return str(
        answers.get("release_title")
        or answers.get("single_track_title")
        or "-"
    )


def build_release_preview(data: dict) -> str:
    is_single = data.get("release_format") == ReleaseFormat.SINGLE.value

    release_block = (
        "👥 <b>Основной артист / артисты:</b>\n"
        f"{escape(str(data.get('main_artists', '-')))}\n\n"
    )

    if is_single:
        release_block += (
            "🎵 <b>Название трека:</b>\n"
            f"{escape(get_release_title_from_answers(data))}\n\n"
        )
    else:
        release_block += (
            "💿 <b>Название релиза:</b>\n"
            f"{escape(get_release_title_from_answers(data))}\n\n"
            "📃 <b>Треки по порядку:</b>\n"
            f"{escape(str(data.get('tracks_order', '-')))}\n\n"
        )

    return (
        "📋 <b>Проверьте заявку перед отправкой</b>\n\n"
        "💼 <b>Дистрибуция:</b> "
        f"{escape(format_distribution_type(data.get('distribution_type')))}\n\n"
        "🎧 <b>Кем вы являетесь:</b> "
        f"{escape(format_artist_type(data.get('artist_type')))}\n\n"
        "📦 <b>Формат релиза:</b> "
        f"{escape(format_release_format(data.get('release_format')))}\n\n"
        f"{release_block}"
        "🔞 <b>Ненормативная лексика:</b> "
        f"{format_explicit(data.get('has_explicit_content'))}\n\n"
        "📅 <b>Дата релиза:</b>\n"
        f"{escape(str(data.get('release_date', '-')))}\n\n"
        "🎼 <b>Жанр:</b>\n"
        f"{escape(str(data.get('genre', '-')))}\n\n"
        "📎 <b>Ссылка на материалы:</b>\n"
        f"{escape(str(data.get('materials_link', '-')))}\n\n"
        "🪪 <b>Имя и фамилия артиста:</b>\n"
        f"{escape(str(data.get('artist_full_name', '-')))}\n\n"
        "💬 <b>Комментарий:</b>\n"
        f"{escape(str(data.get('comment') or '-'))}\n\n"
        "Если всё верно — нажмите <b>Отправить заявку</b>."
    )
