"""
URL configuration for ecuana project.
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from cuaca import views

urlpatterns = [
    # Main endpoint
    path('', views.index, name='index'),
    path('debug/', views.debug_api, name='debug'),
    
    # Include app URLs
    path('cuaca/', include('cuaca.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
