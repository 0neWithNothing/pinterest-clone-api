from django.urls import path, include

from . import views

urlpatterns = [
    path('register/', views.UserCreateAPIView.as_view(), name='register'),
]