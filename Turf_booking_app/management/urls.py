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
    path('block_user/<int:user_id>/',views.block_user,name="block_user"),
    path('Reject_turf/<int:turf_id>/',views.Reject_turf,name="Reject_turf"),
    path('verify_turf/<int:turf_id>/',views.verify_turf,name="verify_turf"),
    path('suspend_toggle/<int:turf_id>/',views.suspend_toggle,name="suspend_toggle"),
    path('warn-user/<int:review_id>/', views.warn_user_view, name='warn_user'),
     path('delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
    
]