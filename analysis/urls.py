from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    path('analyze/', views.analyze_running_video, name='analyze_running_video'),
    path('health/', views.health_check, name='health_check'),
] 