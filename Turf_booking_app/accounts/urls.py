# accounts/urls.py

from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('user-login/', views.user_login, name="user_login"),
    path('admin-login/', views.admin_login, name="admin_login"),
    path('user-register/', views.user_register, name="user_register"),
    path('explore-sports/', views.explore_sports, name="explore_sports"),
    # DELETE THIS LINE BELOW. IT IS THE CAUSE OF THE PROBLEM.
    # path('forget-password/', views.forgot_password, name="forgot_password"),
    path('terms_and_conditions/', views.terms_and_conditions,name="terms_and_conditions"),
    path('privacy_policy/', views.privacy_policy, name="privacy_policy"),
    path('contact_us/', views.contact_us, name="contact_us"),
    path('about_us/', views.about_us, name="about_us"),
    path('cancellation-policy/', views.cancellation_policy,name='cancellation_policy'),
]

# This is the correct set of URLs that you should keep
urlpatterns += [
    path('reset-password/',
         auth_views.PasswordResetView.as_view(
             template_name="registration/password_reset_form.html"
         ),
         name="password_reset"),

    path('reset-password/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name="registration/password_reset_done.html"
         ),
         name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name="registration/password_reset_confirm.html"
         ),
         name="password_reset_confirm"),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name="registration/password_reset_complete.html"
         ),
         name="password_reset_complete"),
]