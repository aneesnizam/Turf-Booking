from . import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('user-login/', views.user_login, name="user_login"),
    path('admin-login/', views.admin_login, name="admin_login"),
    path('user-register/', views.user_register, name="user_register"),
    path('explore-sports/', views.explore_sports, name="explore_sports"),
    path('reset-password/', views.forgot_password, name="forgot_password"),
    # path("user-register/autocomplete-place/",views.autocomplete_place, name="autocomplete_place"),
    path('terms_and_conditions/', views.terms_and_conditions,name="terms_and_conditions"),
    path('privacy_policy/', views.privacy_policy, name="privacy_policy"),
    path('contact_us/', views.contact_us, name="contact_us"),
    path('about_us/', views.about_us, name="about_us"),
    path('cancellation-policy/', views.cancellation_policy,name='cancellation_policy'),





]
