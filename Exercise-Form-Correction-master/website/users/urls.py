# users/urls.py

from django.urls import path
from .views import sign_up

urlpatterns = [
    path('signup/', sign_up.as_view(), name='signup'),
]