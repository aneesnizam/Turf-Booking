from django.urls import path
from . import views

urlpatterns = [
    path('',views.admin_dashboard, name="admin_dashboard"),
    path('users_admin/',views.users_admin, name="users_admin"),
    path('owners_admin/',views.owners_admin, name="owners_admin"),
    path('turfs_admin/',views.turfs_admin, name="turfs_admin"),
    path('bookings_admin/',views.bookings_admin, name="bookings_admin"),
    path('reviews_admin/',views.reviews_admin, name="reviews_admin"),
    
]