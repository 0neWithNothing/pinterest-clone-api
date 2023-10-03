from django.urls import path

from . import views

urlpatterns = [
    path('auth/register/', views.UserCreateAPIView.as_view(), name='register'),
    path('auth/activate/<uidb64>/<token>/', views.UserActivateAPIView.as_view(), name='activate'),
    path('auth/login/', views.LoginViewAPIView.as_view(), name='login'),
    path('auth/logout/', views.LogoutViewAPIView.as_view(), name='logout'),
    path('profile/<slug:slug>/', views.ProfileRetrieveUpdateAPIView.as_view(), name='profile'),
    path('profile/<slug:slug>/follows/', views.FollowAPIView.as_view(), name='follows'),
]