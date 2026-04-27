"""
Run the TikTok collector synchronously on the local machine.
Use this instead of the Celery task when running from a residential IP
(Docker containers are blocked by TikTok's datacenter IP filter).

Usage:
    python manage.py collect_now
"""
import asyncio
import logging

from django.core.management.base import BaseCommand

from trends.models import Country, Platform, Trend, TrendSnapshot

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Collect TikTok US trends directly (run on host machine, not in Docker)'

    def handle(self, *args, **options):
        try:
            platform = Platform.objects.get(slug='tiktok')
            country = Country.objects.get(code='US')
        except (Platform.DoesNotExist, Country.DoesNotExist):
            self.stderr.write(
                self.style.ERROR('Run first: python manage.py seed_platform')
            )
            return

        self.stdout.write('Opening TikTok via Playwright...')

        try:
            hashtag_data, sound_data = asyncio.run(self._fetch())
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Fetch failed: {e}'))
            return

        all_items = [
            (name, 'hashtag', views) for name, views in hashtag_data.items()
        ] + [
            (name, 'sound', views) for name, views in sound_data.items()
        ]

        if not all_items:
            self.stderr.write(self.style.WARNING('No trends returned from TikTok.'))
            return

        for name, trend_type, view_count in all_items:
            trend, _ = Trend.objects.get_or_create(
                name=name,
                platform=platform,
                country=country,
                trend_type=trend_type,
                defaults={'view_count': view_count},
            )
            last = trend.snapshots.order_by('-recorded_at').first()
            viral_score = 0.0
            if last and last.view_count > 0:
                viral_score = (view_count - last.view_count) / last.view_count * 100

            trend.view_count = view_count
            trend.viral_score = viral_score
            trend.save(update_fields=['view_count', 'viral_score'])
            TrendSnapshot.objects.create(trend=trend, view_count=view_count)

        self.stdout.write(self.style.SUCCESS(
            f'Done: {len(all_items)} trends saved '
            f'({len(hashtag_data)} hashtags, {len(sound_data)} sounds)'
        ))

    async def _fetch(self):
        from TikTokApi import TikTokApi

        hashtag_data: dict[str, int] = {}
        sound_data: dict[str, int] = {}

        async with TikTokApi() as api:
            await api.create_sessions(
                num_sessions=1,
                sleep_after=3,
                headless=False,
                suppress_resource_load_types=["image", "media", "font", "stylesheet"],
            )
            self.stdout.write('Session created, fetching trending videos...')

            async for video in api.trending.videos(count=50):
                d = video.as_dict
                play_count: int = d.get('stats', {}).get('playCount', 0)

                for extra in d.get('textExtra', []):
                    tag = extra.get('hashtagName', '').strip()
                    if tag:
                        key = f'#{tag}'
                        hashtag_data[key] = hashtag_data.get(key, 0) + play_count

                music = d.get('music', {})
                title = music.get('title', '').strip() if music else ''
                if title:
                    sound_data[title] = sound_data.get(title, 0) + play_count

        return hashtag_data, sound_data
