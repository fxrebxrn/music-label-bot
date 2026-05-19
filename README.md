# Music Label Telegram Bot

A production-oriented Telegram bot for music labels and artists. It handles release submissions, YouTube Topic linking requests, moderation workflows, FAQ navigation, and role-based admin tools.

## What this bot does

### Artist-facing features
- **Onboarding via `/start`** with an adaptive main menu based on the user role.
- **Profile view** with Telegram identity, role, total submissions, total releases, pending applications, and latest applications.
- **Release submission wizard** (multi-step FSM flow) for:
  - distribution type (paid/free),
  - artist type (singer/producer),
  - release format (single/EP/album),
  - artists list,
  - title,
  - tracklist (for non-singles),
  - explicit content flag,
  - release date,
  - genre,
  - materials link,
  - artist legal name,
  - optional comment.
- **YouTube channel ↔ Topic linking application wizard** with eligibility checklist and a 5-step form.
- **My Applications** section to browse recent applications and open detailed cards.
- **FAQ section** with quick links to royalty info, privacy policy, and terms (configured via environment variables).

### Moderation features
- **Role-protected moderation queue** for moderators and admins.
- Open any pending application and review full details.
- **Approve / reject with a moderator comment**.
- Automatic status sync:
  - application status is updated,
  - linked release status is updated for release applications,
  - user receives a Telegram notification with decision and comment.

### Admin features
- **Admin panel** (role-protected).
- Project statistics: users, applications, pending applications, releases.
- Applications archive (latest items).
- Search application by ID.
- Open full application details.
- Assign user roles (artist / moderator / admin) by username.

## Technical overview

- **Framework:** `aiogram` 3.x
- **Database:** PostgreSQL + SQLAlchemy 2 (async)
- **Migrations:** Alembic
- **Config:** Pydantic Settings (`.env`)
- **Architecture:** handlers → services → repositories
- **State management:** FSM for multi-step flows

## Data model

Main entities:
- `User` — Telegram user profile and role.
- `Release` — normalized release record (including metadata and JSON fields for tracks/artists).
- `Application` — moderation unit for release submissions and account-link requests.

Core enums:
- User roles: `artist`, `moderator`, `admin`
- Application types: `release`, `account_link`
- Statuses: `pending`, `approved`, `rejected`
- Release formats: `single`, `ep`, `album`

## Project structure

```text
app/
  bot/
    handlers/        # Telegram handlers (commands, messages, callbacks)
    keyboards/       # Inline/reply keyboards
    states/          # FSM states
    filters/         # Role-based filters
    middlewares/     # DB session middleware
    loader.py        # Bot + Dispatcher initialization
  db/
    models.py        # SQLAlchemy models
    enums.py         # Domain enums
    database.py      # Engine/session factory
  repositories/      # DB access layer
  services/          # Business logic layer
  utils/             # Formatting helpers
  config.py          # Environment settings
  main.py            # Application entrypoint
alembic/             # DB migrations
```

## Setup

### 1) Clone and create environment

```bash
git clone <your-repo-url>
cd music-label-bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure environment variables

Create `.env` in project root:

```env
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/music_label_bot

LABEL_NAME=Your Label Name
LABEL_LINK=https://t.me/your_label

FAQ_LINK_ROYALTY=https://example.com/royalty
FAQ_LINK_PRIVACY=https://example.com/privacy
FAQ_LINK_TERMS=https://example.com/terms

DEBUG=true
```

### 3) Run migrations

```bash
alembic upgrade head
```

### 4) Start the bot

```bash
python -m app.main
```

## Permissions and access model

- Every Telegram user starts as `artist`.
- Moderator and admin operations are protected by role filters.
- Admins can assign roles through the admin panel.

## Notes for production

- Use webhook mode behind a reverse proxy for high-load production setups (current implementation runs polling).
- Add centralized logging/monitoring.
- Secure secrets using environment management (Vault, Docker secrets, cloud secret managers).
- Consider Redis for FSM storage and caching if you scale horizontally.

## Roadmap (planned)

The following features are planned for future releases:

- **Royalty system**
- **Quarter management**
- **Quarterly reports**
- **Royalty payouts**
- **User balance tracking**

## License

Use is permitted only with the developer's permission.

## AI helping

- README/Docs
- Testing
- Architecture
- Debug
