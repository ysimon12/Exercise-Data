from django.urls import path
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.squat_form_check, name='squat_form_check'),
    path('history', views.history, name='formcheck_history'),
    path('script',views.script,name="script"),
]