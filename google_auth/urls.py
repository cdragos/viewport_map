from django.urls import include, path

from . import views


urlpatterns = [
    path('', views.Auth.as_view(), name='auth'),
    path('oauth2callback', views.AuthCallback.as_view(), name='auth_callback'),
]
