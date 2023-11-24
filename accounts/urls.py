from accounts import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('application/', views.ApplicationView.as_view(), name='application'),
    path('profile/', views.ProfileView.as_view(), name='profile')
]