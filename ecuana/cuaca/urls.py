"""
URL configuration untuk app 'cuaca'
"""

from django.urls import path
from . import views

app_name = 'cuaca'

urlpatterns = [
    path('', views.index, name='index'),
    path('tentang/', views.tentang, name='tentang'),
    path('api/debug/', views.debug_api, name='debug_api'),
]
