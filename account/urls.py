"""
URL configuration for swanapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from account.views import UserRegistrationView, UserLoginView, SendPasswordResetEmailView, UserChangePasswordView, UserPasswordResetView, UserProfileView, UpdateUserView, UpdateProfilePictureView, ChangeEmailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', UserLoginView.as_view(), name="login"),
    path('update_picture/', UpdateProfilePictureView.as_view(), name='update_profile'),
    path('change-email/', ChangeEmailView.as_view(), name='Change-email'),
    path('me/', UserProfileView.as_view(), name="profile"),
    path('update/', UpdateUserView.as_view(), name='update_profile'),
    path('send-reset-password-mail/', SendPasswordResetEmailView.as_view(), name="reset_password_email"),
    path('changepassword/', UserChangePasswordView.as_view(), name="changepassword"),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name="reset-password"),

]
