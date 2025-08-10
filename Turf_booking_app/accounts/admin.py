from django.contrib import admin
from .models import User, Turf ,Sport


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'fullname', 'phone', 'is_active', 'is_staff', 'role','latitude','longitude'
    )
    list_filter = ('is_staff', 'role', 'is_active')
    search_fields = ('fullname', 'email')

@admin.register(Turf)
class TurfAdmin(admin.ModelAdmin):
    list_display = (
        'turf_name', 'owner', 'contact_number', 'cost_per_hour',
        'verification_status', 'created_at','latitude','longitude'
    )
    list_filter = ('verification_status', 'created_at')
    search_fields = ('turf_name', 'owner__email', 'contact_number')

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields=('name',)