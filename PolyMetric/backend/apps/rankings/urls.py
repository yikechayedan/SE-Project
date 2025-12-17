from django.urls import path
from . import views

app_name = 'rankings'

urlpatterns = [
    path('update/', views.update_rankings, name='update_rankings'),
    path('top/', views.top_models, name='top_models'),
    path('history/<int:model_id>/', views.model_ranking_history, name='model_ranking_history'),
]