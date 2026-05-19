from datetime import datetime
from app.db.enums import ApplicationStatus, ApplicationType, UserRole

ROLE_TITLES = {
    UserRole.ARTIST: "Артист",
    UserRole.MODERATOR: "Модератор",
    UserRole.ADMIN: "Админ",
}

APPLICATION_TYPE_TITLES = {
    ApplicationType.RELEASE: "Релиз",
    ApplicationType.ACCOUNT_LINK: "Связка аккаунта",
}

APPLICATION_STATUS_TITLES = {
    ApplicationStatus.PENDING: 'На модерации <tg-emoji emoji-id="5843770423203861696">⏺</tg-emoji>',
    ApplicationStatus.APPROVED: 'Принята <tg-emoji emoji-id="5843882633519437060">⏺</tg-emoji>',
    ApplicationStatus.REJECTED: 'Отклонена <tg-emoji emoji-id="5841193060574171492">⏺</tg-emoji>',
}

def format_datetime(value: datetime) -> str:
    return value.strftime("%d.%m.%Y %H:%M")


def format_user_role(role: UserRole) -> str:
    return ROLE_TITLES.get(role, role.value)


def format_application_type(application_type: ApplicationType) -> str:
    return APPLICATION_TYPE_TITLES.get(application_type, application_type.value)


def format_application_status(status: ApplicationStatus) -> str:
    return APPLICATION_STATUS_TITLES.get(status, status.value)
