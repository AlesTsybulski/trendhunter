import asyncio
import logging

from celery import shared_task
from django.utils import timezone

from .models import Country, Platform, Trend, TrendSnapshot

logger = logging.getLogger(__name__)


async def _fetch_tiktok_trends():
    """
    Open a headless Chromium session via TikTokApi, pull the global
    trending feed, and return aggregated view counts per hashtag and sound.
    """
    from TikTokApi import TikTokApi

    hashtag_data: dict[str, int] = {}
    sound_data: dict[str, int] = {}

    async with TikTokApi() as api:
        await api.create_sessions(
            num_sessions=1,
            sleep_after=3,
            headless=True,
        )
        async for video in api.trending.videos(count=50):
            d = video.as_dict
            play_count: int = d.get('stats', {}).get('playCount', 0)

            # Hashtags — TikTok stores them in textExtra
            for extra in d.get('textExtra', []):
                tag = extra.get('hashtagName', '').strip()
                if tag:
                    key = f'#{tag}'
                    hashtag_data[key] = hashtag_data.get(key, 0) + play_count

            # Sound / music track
            music = d.get('music', {})
            title = music.get('title', '').strip() if music else ''
            if title:
                sound_data[title] = sound_data.get(title, 0) + play_count

    return hashtag_data, sound_data


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
)
def collect_trends(self):
    try:
        platform = Platform.objects.get(slug='tiktok')
        country = Country.objects.get(code='US')
    except (Platform.DoesNotExist, Country.DoesNotExist):
        logger.error(
            "seed data missing — run: python manage.py seed_platform"
        )
        # Don't retry; this is a config error, not a transient failure.
        return 0

    try:
        hashtag_data, sound_data = asyncio.run(_fetch_tiktok_trends())
    except Exception as exc:
        logger.exception("TikTok fetch failed: %s", exc)
        raise

    all_items = [
        (name, 'hashtag', views) for name, views in hashtag_data.items()
    ] + [
        (name, 'sound', views) for name, views in sound_data.items()
    ]

    if not all_items:
        logger.warning("collect_trends: API returned no data")
        return 0

    for name, trend_type, view_count in all_items:
        trend, _ = Trend.objects.get_or_create(
            name=name,
            platform=platform,
            country=country,
            trend_type=trend_type,
            defaults={'view_count': view_count},
        )

        last = trend.snapshots.order_by('-recorded_at').first()
        if last and last.view_count > 0:
            viral_score = (view_count - last.view_count) / last.view_count * 100
        else:
            viral_score = 0.0

        trend.view_count = view_count
        trend.viral_score = viral_score
        trend.save(update_fields=['view_count', 'viral_score'])

        TrendSnapshot.objects.create(trend=trend, view_count=view_count)

    logger.info(
        "collect_trends done: %d trends (%d hashtags, %d sounds)",
        len(all_items), len(hashtag_data), len(sound_data),
    )
    return len(all_items)
