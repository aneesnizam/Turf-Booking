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
    path("autocomplete-place/",view1.autocomplete_place, name="autocomplete_place"),
    path('update-location/', views.update_user_location,name='update_user_location'),
    path('favorites/', views.favorites, name="favorites"),
    path('toggle-favourite/<int:turf_id>/',views.toggle_favourite, name='toggle_favourite'),
    path('ajax/check-availability/<int:turf_id>/',views.check_availability, name='check_availability'),
    path('view_booking_detail/<str:booking_token>',views.view_booking_detail, name="view_booking_detail"),
    path('submit-rating/', views.submit_rating, name='submit_rating'),
    path('invoice/<int:booking_id>/',views.generate_invoice_pdf, name='invoice_pdf'),
    path('cancel-booking/<int:booking_id>/',views.cancel_booking, name="cancel_booking"),
    path('bookings/<str:booking_token>/qr/',views.booking_qr, name="booking_qr"),
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('profile_settings/',views.profile_settings,name="profile_settings"),
    path('recent_bookings/',views.recent_bookings,name="recent_bookings"),
    path('owner_dashboard/delete_turf/<int:turf_id>/', views.delete_turf, name="delete_turf"),
    path('owner_dashboard/edit_turf/<int:turf_id>/', views.edit_turf, name="edit_turf"),
    path('owner_dashboard/delete_image/<int:image_id>/', views.delete_image, name="delete_image"),
    
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
