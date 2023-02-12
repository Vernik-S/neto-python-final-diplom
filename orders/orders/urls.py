"""orders URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from allauth.socialaccount.providers.github.views import oauth2_login, oauth2_callback
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from my_app.views import GitHubLogin, CodeView

swagger_patterns = [
    # YOUR PATTERNS
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('my_app.urls', namespace='my_app')),
    path('api/v1/', include(swagger_patterns)),
    # path('auth/', include('rest_auth.urls')),
    path('accounts/', include('allauth.urls')),  # new
    # path('rest-auth/github/', GitHubLogin.as_view(),     name='redirect'),
    # path('api/v1/code', CodeView, name='code'),
    # path('auth/get_token/',  GitHubLogin.as_view(), name='get-token'),
    # path('', oauth2_login),

    path('auth/github/login/callback/', GitHubLogin.as_view(), name='github_callback'),

    # path('auth/github/callback/', oauth2_callback, name='github_callback'),




]
