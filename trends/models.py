from django.db import models


class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Trend(models.Model):
    TYPE_CHOICES = [('hashtag', 'Hashtag'), ('sound', 'Sound')]

    name = models.CharField(max_length=255)
    trend_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    platform = models.ForeignKey(Platform, on_delete=models.PROTECT)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)

    viral_score = models.FloatField(default=0.0, db_index=True)
    view_count = models.BigIntegerField(default=0)

    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'platform', 'country', 'trend_type'],
                name='unique_trend',
            )
        ]
        indexes = [
            models.Index(fields=['country', 'platform', '-viral_score']),
        ]

    def __str__(self):
        return f"{self.name} [{self.trend_type}] — {self.platform} / {self.country}"


class TrendSnapshot(models.Model):
    trend = models.ForeignKey(Trend, on_delete=models.CASCADE, related_name='snapshots')
    view_count = models.BigIntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.trend.name} snapshot @ {self.recorded_at:%Y-%m-%d %H:%M}"
