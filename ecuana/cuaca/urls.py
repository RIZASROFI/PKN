"""
URL configuration untuk app 'cuaca'
"""

from django.urls import path
from . import views

app_name = 'cuaca'

urlpatterns = [
    path('', views.index, name='index'),
]
