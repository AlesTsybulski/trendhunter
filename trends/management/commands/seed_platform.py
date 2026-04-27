from django.core.management.base import BaseCommand
from trends.models import Platform, Country


class Command(BaseCommand):
    help = 'Seed TikTok and US rows required by the collector'

    def handle(self, *args, **options):
        platform, created = Platform.objects.get_or_create(
            slug='tiktok',
            defaults={'name': 'TikTok'},
        )
        self.stdout.write(
            self.style.SUCCESS(f'Platform: {platform}  ({"created" if created else "already exists"})')
        )

        country, created = Country.objects.get_or_create(
            code='US',
            defaults={'name': 'United States'},
        )
        self.stdout.write(
            self.style.SUCCESS(f'Country:  {country}  ({"created" if created else "already exists"})')
        )
