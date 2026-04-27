from django.contrib import admin
from django.urls import path, include
from trends.views import DashboardView
from users.views import login_page, register_page, logout_view

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('users/login/', login_page, name='login'),
    path('users/register/', register_page, name='register'),
    path('users/logout/', logout_view, name='logout'),
    path('admin/', admin.site.urls),
    path('api/trends/', include('trends.urls')),
    path('api/users/', include('users.urls')),
]
