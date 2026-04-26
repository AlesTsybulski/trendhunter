from django.shortcuts import render
from django.views import View
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Trend
from .serializers import TrendSerializer, TrendDetailSerializer


class TrendListView(generics.ListAPIView):
    serializer_class = TrendSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ('trend_type',)
    ordering_fields = ('viral_score', 'view_count', 'collected_at')
    ordering = ('-viral_score',)

    def get_queryset(self):
        return Trend.objects.select_related('platform', 'country').all()


class TrendDetailView(generics.RetrieveAPIView):
    serializer_class = TrendDetailSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Trend.objects.prefetch_related('snapshots').select_related('platform', 'country')


class DashboardView(View):
    def get(self, request):
        trend_type = request.GET.get('trend_type', '')
        qs = Trend.objects.select_related('platform', 'country').order_by('-viral_score')
        if trend_type in ('hashtag', 'sound'):
            qs = qs.filter(trend_type=trend_type)

        trends = list(qs[:50])
        max_score = trends[0].viral_score if trends else 1

        ctx = {
            'trends': trends,
            'max_score': max_score,
            'active_filter': trend_type,
        }

        if request.headers.get('HX-Request'):
            return render(request, 'partials/trend_content.html', ctx)

        return render(request, 'trends/index.html', ctx)
