from . import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('user-login/', views.user_login, name="user_login"),
    path('admin-login/', views.admin_login, name="admin_login"),
    path('user-register/', views.user_register, name="user_register"),
     path('explore-sports/', views.explore_sports, name="explore_sports"),
     path('reset-password/', views.forgot_password, name="forgot_password"),
     path("user-register/autocomplete-place/", views.autocomplete_place, name="autocomplete_place"),
     




]
