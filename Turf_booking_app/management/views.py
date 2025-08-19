from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required,user_passes_test
import json
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
from accounts.models import Booking,User,Turf,Rating
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()



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
    
    owners_count =  User.objects.filter(role = 'owner').count()
    users_count = User.objects.filter(is_staff = False).count()
    total_bookings = Booking.objects.count()
    pending_turfs = Turf.objects.filter(verification_status = 'pending')
    pending_turfs_count = pending_turfs.count()
    latest_reviews = Rating.objects.order_by('-created_at')[:5]
    



    context = {
        'chart_data_json': chart_data_json,
        'users_count':users_count,
        'owners_count':owners_count,
        'total_bookings':total_bookings,
        'pending_turfs_count':pending_turfs_count,
        'pending_turfs':pending_turfs,
        'latest_reviews':latest_reviews
    }
    
    return render(request,'_dashboard_admin.html',context)

    

@user_passes_test(lambda u: u.is_staff)
@login_required
def users_admin(request):
    # Start with the base query: get all non-staff users.
    users = User.objects.filter(is_staff=False).order_by('-joined')

    # --- Search Logic ---
    search_query = request.GET.get('q')
    if search_query:
        users = users.filter(
            Q(fullname__icontains=search_query) | 
            Q(email__icontains=search_query)
        )

    # --- Filter Logic ---
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)

    status_filter = request.GET.get('status')
    if status_filter == 'active':
        users = users.filter(is_blocked=False)   # ✅ changed
    elif status_filter == 'blocked':
        users = users.filter(is_blocked=True)    # ✅ changed

    joined_filter = request.GET.get('joined')
    today = timezone.now().date()
    if joined_filter == 'today':
        users = users.filter(joined__date=today)
    elif joined_filter == 'week':
        start_of_week = today - timedelta(days=7)
        users = users.filter(joined__date__gte=start_of_week)
    elif joined_filter == 'month':
        start_of_month = today - timedelta(days=30)
        users = users.filter(joined__date__gte=start_of_month)

    context = {
        'users': users
    }
    
    return render(request, '_users_admin.html', context)




@user_passes_test(lambda u: u.is_staff)
@login_required
def turfs_admin(request):
    return render(request,'_turfs_admin.html')



@user_passes_test(lambda u: u.is_staff)
@login_required
def bookings_admin(request):
    return render(request,'_bookings_admin.html')



@login_required
@user_passes_test(lambda u: u.is_staff)
def block_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)

        # ✅ Only toggle is_blocked
        user.is_blocked = not user.is_blocked
        user.save()

        status = "unblocked" if not user.is_blocked else "blocked"
        return JsonResponse({"success": True, "message": f"User {status} successfully."})
    
    return JsonResponse({"success": False, "message": "Invalid request."}, status=400)



@user_passes_test(lambda u: u.is_staff)
@login_required
def reviews_admin(request):
    return render(request,'_reviews_admin.html')




@user_passes_test(lambda u: u.is_staff)
@login_required
def approve_turf(request,turf_id):
    turf = get_object_or_404(Turf,id=turf_id)
    if turf:
        turf.verification_status = 'verified'
        turf.save()
        return JsonResponse({"status": "approved"})
    return redirect('admin_dashboard')



@user_passes_test(lambda u: u.is_staff)
@login_required
def reject_turf(request,turf_id):
    turf = get_object_or_404(Turf,id=turf_id)
    if turf:
        turf.verification_status = 'declined'
        turf.save()
        return JsonResponse({"status": "declined"})
    return redirect('admin_dashboard')


