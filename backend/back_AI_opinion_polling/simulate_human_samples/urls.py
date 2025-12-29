"""
URL configuration for simulate_human_samples project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from allauth.account.views import confirm_email
from rest_framework_simplejwt.views import TokenRefreshView
from dj_rest_auth.views import LogoutView, PasswordResetView
from user.views import CustomJWTLoginView,SignupAPIView
from dj_rest_auth.views import PasswordResetConfirmView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)







urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('auth/registration/account-confirm-email/<str:key>/', confirm_email, name='account_confirm_email_html'),
    # path('auth/registration/', SignupAPIView.as_view(), name='rest_register'),
    path('auth/login/', CustomJWTLoginView.as_view(), name='rest_login'),
    path('auth/logout/', LogoutView.as_view(), name='rest_logout'),
    path('auth/password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('auth/password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("accounts/", include("allauth.urls")),
    path('auth/google/', include('allauth.socialaccount.providers.google.urls')),
    path('project/', include('project.urls'), name='project'),
]
