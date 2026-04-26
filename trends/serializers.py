from rest_framework import serializers
from .models import Trend, TrendSnapshot


class TrendSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendSnapshot
        fields = ('id', 'view_count', 'recorded_at')


class TrendSerializer(serializers.ModelSerializer):
    platform = serializers.StringRelatedField()
    country = serializers.StringRelatedField()

    class Meta:
        model = Trend
        fields = ('id', 'name', 'trend_type', 'platform', 'country', 'viral_score', 'view_count', 'collected_at')


class TrendDetailSerializer(TrendSerializer):
    snapshots = TrendSnapshotSerializer(many=True, read_only=True)

    class Meta(TrendSerializer.Meta):
        fields = TrendSerializer.Meta.fields + ('snapshots',)
