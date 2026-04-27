# TrendHunter

A Django-based dashboard for tracking trending TikTok hashtags and sounds in the United States.

## Stack

- **Django 6** — web framework + HTML templates
- **HTMX** — dynamic filtering without JavaScript
- **PostgreSQL 16** — database
- **Celery 5 + Redis** — task queue for scheduled collection
- **Docker Compose** — runs all services

## The Data Collection Problem

TikTok aggressively blocks automated access from non-residential IP addresses. This affects:

- **Docker containers** — their outbound IPs are in datacenter ranges, which TikTok blocks entirely
- **VPN connections** — VPN server IPs are treated the same as datacenter IPs
- **`TikTokApi` (unofficial Python library)** — uses Playwright to open a real Chromium browser and visit `tiktok.com` to obtain session tokens. Even from a residential IP, TikTok's bot detection identifies the automated browser and blocks the JS initialization that the library depends on. The page technically loads (`load` event fires) but TikTok never sets the internal state objects `TikTokApi` waits for, causing a timeout.

### Solution

The cleanest path to real data is a third-party scraping service that runs from residential IPs with proper anti-bot evasion built in:

- **Apify** (`apify.com`) — has a dedicated TikTok scraper actor, free $5 credit, simple HTTP API. You trigger a run via one POST request and poll for results.
- **RapidAPI TikTok scrapers** — several options with free tiers (100–500 req/month). Look for endpoints that return trending hashtags/sounds directly.

The collector task lives in `trends/tasks.py` (`collect_trends`). Replace the `_fetch_tiktok_trends()` function with an `httpx` call to whichever service you choose — the rest of the pipeline (upsert, viral score, snapshots) stays the same.

For development, fake data can be seeded with the management command described below.

## Setup

### Requirements

- Docker Desktop
- Python 3.12+ with a virtual environment (for running the collector locally)

### 1. Clone and configure

```bash
git clone <repo-url>
cd trendhunter
cp .env.example .env   # fill in your values
```

Minimum `.env`:

```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=trendhunter
DB_USER=user
DB_PASSWORD=password
DB_HOST=postgres
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
```

### 2. Start Docker services

```bash
docker compose up -d
```

This starts: `web` (port 8000), `worker`, `beat`, `flower` (port 5555), `postgres`, `redis`.

### 3. Run migrations

```bash
docker compose exec web python manage.py migrate
```

### 4. Create admin user (optional)

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Seed platform and country rows

Required before any data collection:

```bash
docker compose exec web python manage.py seed_platform
```

### 6. Load development data

Since real TikTok collection requires a third-party API (see above), seed realistic fake trends to see the dashboard working:

```bash
docker compose exec web python manage.py seed_fake_data
```

To reset and re-seed:

```bash
docker compose exec web python manage.py seed_fake_data --clear
```

## Using the App

Open `http://localhost:8000`.

- **Home page** — shown to unauthenticated visitors with a sign-up CTA
- **Register** at `/users/register/` or **log in** at `/users/login/`
- **Dashboard** — after login, shows the top 50 US trends sorted by viral score
- **Filter tabs** — switch between ALL / HASHTAGS / SOUNDS without a page reload (HTMX)
- **Viral score** — percentage growth in views since the previous collection run. Amber = very hot (≥200%), green = growing

## Connecting Real Data

Once you have an API key from Apify or RapidAPI:

1. Add `RAPIDAPI_KEY` or `APIFY_TOKEN` to `.env`
2. Update `_fetch_tiktok_trends()` in `trends/tasks.py` to call the API via `httpx`
3. Register `collect_trends` as a periodic task in Django admin → **Periodic Tasks** (hourly recommended)
4. Celery Beat will run it automatically

## Services

| URL | Service |
|-----|---------|
| `http://localhost:8000` | Web app |
| `http://localhost:5555` | Flower (Celery monitor) |
| `http://localhost:5433` | PostgreSQL (exposed for local tools) |
