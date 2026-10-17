from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Стандартные маршруты авторизации (login, logout)
    path('accounts/', include('django.contrib.auth.urls')),

    # Маршруты приложения
    path('accounts/', include('accounts.urls')),
    path('', include('accounts.urls')),

    path('tickets/', include('tickets.urls')),
]
