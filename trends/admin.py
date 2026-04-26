from django.contrib import admin
from .models import Platform, Country, Trend, TrendSnapshot


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Trend)
class TrendAdmin(admin.ModelAdmin):
    list_display = ('name', 'trend_type', 'platform', 'country', 'viral_score', 'view_count', 'collected_at')
    list_filter = ('trend_type', 'platform', 'country')
    search_fields = ('name',)
    ordering = ('-viral_score',)


@admin.register(TrendSnapshot)
class TrendSnapshotAdmin(admin.ModelAdmin):
    list_display = ('trend', 'view_count', 'recorded_at')
    list_filter = ('trend__country', 'trend__platform')
    ordering = ('-recorded_at',)
