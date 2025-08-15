from django.shortcuts import render
from django.contrib.auth.decorators import login_required,user_passes_test
import json
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
from accounts.models import Booking


# Create your views here.
@user_passes_test(lambda u: u.is_staff)
@login_required
def admin_dashboard(request):
    weeks_ago = timezone.now().date() - timedelta(weeks=1)

    # 2. USE TRUNCWEEK: Group bookings by week and count them
    bookings_data = Booking.objects.filter(created_at__gte=weeks_ago) \
        .annotate(week=TruncDay('created_at')) \
        .values('week') \
        .annotate(count=Count('id')) \
        .order_by('week')

    # 2. USE TRUNCWEEK: Group bookings by week and sum their total_cost
    revenue_data = Booking.objects.filter(created_at__gte=weeks_ago) \
        .annotate(week=TruncDay('created_at')) \
        .values('week') \
        .annotate(total=Sum('total_cost')) \
        .order_by('week')

    # 3. UPDATE LABELS: Format the week's start date as "11 Aug"
    booking_labels = [b['week'].strftime('%d %b') for b in bookings_data]
    booking_counts = [b['count'] for b in bookings_data]
    
    revenue_labels = [r['week'].strftime('%d %b') for r in revenue_data]
    revenue_totals = [float(r['total']) if r['total'] else 0 for r in revenue_data]
  
    chart_data_json = json.dumps({
        'booking_labels': booking_labels,
        'booking_data': booking_counts,
        'revenue_labels': revenue_labels,
        'revenue_data': revenue_totals,
    })

    context = {
        'chart_data_json': chart_data_json,
    }
    
    return render(request,'_dashboard_admin.html',context)



@user_passes_test(lambda u: u.is_staff)
@login_required
def users_admin(request):
    return render(request,'_users_admin.html')



@user_passes_test(lambda u: u.is_staff)
@login_required
def owners_admin(request):
    return render(request,'_owners_admin.html')



@user_passes_test(lambda u: u.is_staff)
@login_required
def turfs_admin(request):
    return render(request,'_turfs_admin.html')



@user_passes_test(lambda u: u.is_staff)
@login_required
def bookings_admin(request):
    return render(request,'_bookings_admin.html')



@user_passes_test(lambda u: u.is_staff)
@login_required
def reviews_admin(request):
    return render(request,'_reviews_admin.html')