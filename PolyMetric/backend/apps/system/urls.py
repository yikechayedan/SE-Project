from django.urls import path
from . import views

app_name = 'system'

urlpatterns = [
    path('news/', views.news_feed, name='news_feed'),
]