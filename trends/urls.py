from django.urls import path
from .views import TrendListView, TrendDetailView

app_name = 'trends'

urlpatterns = [
    path('', TrendListView.as_view(), name='trend-list'),
    path('<int:pk>/', TrendDetailView.as_view(), name='trend-detail'),
]
