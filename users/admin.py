from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Используем стандартный интерфейс админки, но для нашей модели
admin.site.register(User, UserAdmin)