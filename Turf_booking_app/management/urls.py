from django.urls import path
from . import views

urlpatterns = [
    path('',views.admin_dashboard, name="admin_dashboard"),
    path('users_admin/',views.users_admin, name="users_admin"),
    path('turfs_admin/',views.turfs_admin, name="turfs_admin"),
    path('bookings_admin/',views.bookings_admin, name="bookings_admin"),
    path('reviews_admin/',views.reviews_admin, name="reviews_admin"),
    path('approve_turf/<int:turf_id>/',views.approve_turf, name="approve_turf"),
       path('reject_turf/<int:turf_id>/',views.reject_turf, name="reject_turf"),
       path('block_user/<int:user_id>/',views.block_user,name="block_user")
    
]