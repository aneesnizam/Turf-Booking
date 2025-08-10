from . import views
from accounts import views as view1
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', view1.landing_page, name="landing"),
    path('home/', views.home, name="home"),
    path('turfs/', views.turfs, name="turfs"),
    path('booking/', views.booking, name="booking"),
    path('profile/', views.profile, name="profile"),
    path('logout/', views.logoutuser, name="logout"),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/changepassword/', views.change_password, name="change_password"),
    path('turf_register/', views.turf_register, name="turf_register"),
    path('owner_dashboard/', views.owner_dashboard, name="owner_dashboard"),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),
    path('turf_details/<int:turf_id>', views.turf_details, name="turf_details"),
    path("turf_register/autocomplete-place/",
         view1.autocomplete_place, name="autocomplete_place"),
    path('update-location/', views.update_user_location,
         name='update_user_location'),
    path('favorites/', views.favorites, name="favorites"),
    path('toggle-favourite/<int:turf_id>/',
         views.toggle_favourite, name='toggle_favourite'),
    path('ajax/check-availability/<int:turf_id>/',
         views.check_availability, name='check_availability'),
    path('terms_and_conditions/', views.terms_and_conditions,
         name="terms_and_conditions"),
    path('privacy_policy/', views.privacy_policy, name="privacy_policy"),
    path('contact_us/', views.contact_us, name="contact_us"),
    path('about_us/', views.about_us, name="about_us"),
      path('cancellation-policy/', views.cancellation_policy, name='cancellation_policy'),
       path('view_booking_detail/<str:booking_token>', views.view_booking_detail, name="view_booking_detail"),
       path('submit-rating/', views.submit_rating, name='submit_rating'),
         path('invoice/<int:booking_id>/', views.generate_invoice_pdf, name='invoice_pdf'),
         path('cancel-booking/<int:booking_id>/',views.cancel_booking,name="cancel_booking"),
         path('bookings/<str:booking_token>/qr/',views.booking_qr,name="booking_qr")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
