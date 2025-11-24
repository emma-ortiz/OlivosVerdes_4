# backend_olivos/urls.py

from django.contrib import admin
from django.urls import path, include 
from django.conf.urls.static import static # <-- Importación necesaria
from django.conf import settings # <-- Importación necesaria

urlpatterns = [
    path('admin/', admin.site.urls),
    # Conecta las URLs de tu aplicación 'app_fruteria'
    path('', include('app_fruteria.urls')), 
]

# 🚨 CONFIGURACIÓN NECESARIA PARA SERVIR ARCHIVOS DE USUARIO (MEDIA) EN DESARROLLO 🚨
if settings.DEBUG:
    # Esto le dice a Django dónde buscar los archivos MEDIA_URL
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Opcional: Esto ayuda si tienes problemas con los archivos STATIC
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)