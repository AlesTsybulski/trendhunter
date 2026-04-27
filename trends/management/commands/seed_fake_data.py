"""
Development helper — seeds realistic-looking TikTok US trend data.
Use this when running inside Docker (datacenter IPs are blocked by TikTok).
"""
import random
from django.core.management.base import BaseCommand
from trends.models import Platform, Country, Trend, TrendSnapshot


HASHTAGS = [
    "#fyp", "#foryoupage", "#viral", "#trending", "#tiktok",
    "#dance", "#comedy", "#fashion", "#food", "#travel",
    "#motivation", "#aesthetic", "#skincare", "#fitness", "#gaming",
    "#cooking", "#art", "#music", "#diy", "#pets",
    "#ootd", "#makeup", "#workout", "#vlog", "#storytime",
    "#mindset", "#hustle", "#entrepreneur", "#crypto", "#nfl",
]

SOUNDS = [
    "Espresso - Sabrina Carpenter",
    "Die With A Smile - Lady Gaga, Bruno Mars",
    "APT. - ROSÉ & Bruno Mars",
    "luther - Kendrick Lamar",
    "Birds of a Feather - Billie Eilish",
    "original sound - creator_vibes",
    "BIRDS OF A FEATHER sped up",
    "A Bar Song (Tipsy) - Shaboozey",
    "Good Luck, Babe! - Chappell Roan",
    "Too Sweet - Hozier",
    "Fortnight - Taylor Swift",
    "Not Like Us - Kendrick Lamar",
    "360 - Charli xcx",
    "Feather - Sabrina Carpenter",
    "Taste - Sabrina Carpenter",
]


class Command(BaseCommand):
    help = 'Seed fake TikTok US trends for development/testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing trends before seeding',
        )

    def handle(self, *args, **options):
        try:
            platform = Platform.objects.get(slug='tiktok')
            country = Country.objects.get(code='US')
        except (Platform.DoesNotExist, Country.DoesNotExist):
            self.stderr.write(
                self.style.ERROR('Run seed_platform first: python manage.py seed_platform')
            )
            return

        if options['clear']:
            deleted, _ = Trend.objects.filter(platform=platform, country=country).delete()
            self.stdout.write(f'Cleared {deleted} existing trends.')

        created_count = 0

        for name in HASHTAGS:
            view_count = random.randint(50_000_000, 8_000_000_000)
            prev_views = int(view_count * random.uniform(0.7, 0.98))
            viral_score = (view_count - prev_views) / prev_views * 100

            trend, created = Trend.objects.get_or_create(
                name=name,
                platform=platform,
                country=country,
                trend_type='hashtag',
                defaults={'view_count': view_count, 'viral_score': viral_score},
            )
            if not created:
                trend.view_count = view_count
                trend.viral_score = viral_score
                trend.save(update_fields=['view_count', 'viral_score'])

            TrendSnapshot.objects.create(trend=trend, view_count=prev_views)
            TrendSnapshot.objects.create(trend=trend, view_count=view_count)
            created_count += 1

        for name in SOUNDS:
            view_count = random.randint(10_000_000, 2_000_000_000)
            prev_views = int(view_count * random.uniform(0.6, 0.95))
            viral_score = (view_count - prev_views) / prev_views * 100

            trend, created = Trend.objects.get_or_create(
                name=name,
                platform=platform,
                country=country,
                trend_type='sound',
                defaults={'view_count': view_count, 'viral_score': viral_score},
            )
            if not created:
                trend.view_count = view_count
                trend.viral_score = viral_score
                trend.save(update_fields=['view_count', 'viral_score'])

            TrendSnapshot.objects.create(trend=trend, view_count=prev_views)
            TrendSnapshot.objects.create(trend=trend, view_count=view_count)
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded {created_count} trends ({len(HASHTAGS)} hashtags, {len(SOUNDS)} sounds)'
            )
        )
