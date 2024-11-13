from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api_wpp.urls')),  # Inclui as rotas do app `api_wpp`
]
