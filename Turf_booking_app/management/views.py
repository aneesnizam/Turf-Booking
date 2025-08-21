from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required,user_passes_test
import json
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
from accounts.models import Booking,User,Turf,Rating,Sport
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
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
        users = users.filter(joined=today)
    elif joined_filter == 'week':
        start_of_week = today - timedelta(days=7)
        users = users.filter(joined__gte=start_of_week)
    elif joined_filter == 'month':
        start_of_month = today - timedelta(days=30)
        users = users.filter(joined__gte=start_of_month)
    
    paginator = Paginator(users,10)
    page_number = request.GET.get('page')
    datas = paginator.get_page(page_number)

    context = {
        'users': datas
    }
    
    return render(request, '_users_admin.html', context)



@user_passes_test(lambda u: u.is_staff)
@login_required
def turfs_admin(request):
    # Start with an optimized base query
    turfs = Turf.objects.select_related('owner').prefetch_related('sports')

    # --- Search ---
    q = request.GET.get("q")
    if q:
        turfs = turfs.filter(turf_name__icontains=q)

    # --- Filters (Logic is unchanged) ---
    status = request.GET.get("status")
    if status:
        turfs = turfs.filter(status=status)

    verification = request.GET.get("verification")
    if verification:
        if verification != 'suspended':
            turfs = turfs.filter(verification_status=verification, is_suspended=False)
        else:
            turfs = turfs.filter(is_suspended=True)

    district = request.GET.get("district", '')
    if district:
        turfs = turfs.filter(district=district)
      

    sport = request.GET.get("sport")
    if sport:
        turfs = turfs.filter(sports__name__iexact=sport)

    # Remove duplicates and order the results for consistent pagination
    turfs = turfs.distinct().order_by('-created_at')
    
    # These queries are for the form dropdowns and are fine as they are
    all_sports = Sport.objects.all()
    all_districts = Turf.objects.values_list('district', flat=True).order_by('district').distinct()
    
    paginator = Paginator(turfs, 10)
    page_number = request.GET.get('page')
    paginated_turfs = paginator.get_page(page_number)

    form_datas = {
        'status': status,
        'verification': verification,
        'district': district,
        'sport': sport,
    }
    context = {
        "turfs": paginated_turfs,
        'form_datas': form_datas,
        'all_sports': all_sports,
        'all_districts': all_districts,
    }
    return render(request, "_turfs_admin.html", context)



@login_required
@user_passes_test(lambda u: u.is_staff)
def block_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
   
        user.is_blocked = not user.is_blocked
        user.save()

        turfs = Turf.objects.filter(owner=user)

        if user.is_blocked:
            turfs.update(is_suspended=True)
            
        else:
            turfs.update(is_suspended=False)

        status = "blocked" if user.is_blocked else "unblocked"
        message = f"User has been {status} successfully."
        
        return JsonResponse({"success": True, "message": message})
    
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)


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


@user_passes_test(lambda u: u.is_staff)
@login_required
def suspend_toggle(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    turf.is_suspended = not turf.is_suspended
    turf.save()
    return redirect('turfs_admin')


def verify_turf(request,turf_id):
    turf = get_object_or_404(Turf,id=turf_id)
    turf.verification_status = 'verified'
    turf.save()
    return redirect('turfs_admin')


def Reject_turf(request,turf_id):
    turf = get_object_or_404(Turf,id=turf_id)
    if turf.verification_status == 'declined':
        turf.verification_status = 'pending'
    else:
        turf.verification_status = 'declined'
    turf.save()
    return redirect('turfs_admin')



@login_required
@user_passes_test(lambda u: u.is_staff)
def bookings_admin(request):

    bookings_list = Booking.objects.select_related('user', 'turf')

    # Get filter parameters from the URL
    q = request.GET.get('q')
    date_range = request.GET.get('date_range')
    turfname = request.GET.get('turf_name')
    user_email = request.GET.get('user_email')
    
    # --- Apply Filters ---
    if q:
        bookings_list = bookings_list.filter(
            Q(user__fullname__icontains=q) |
            Q(user__email__icontains=q) |
            Q(turf__turf_name__icontains=q) |
            Q(id__icontains=q) |
            Q(turf__place__icontains=q) |
            Q(turf__district__icontains=q)
        )
    
    if turfname:
        bookings_list = bookings_list.filter(turf__turf_name=turfname)
        
    if user_email:
        bookings_list = bookings_list.filter(user__email=user_email)
    
    if date_range:
        today = timezone.now().date()
        if date_range == "today":
            bookings_list = bookings_list.filter(created_at=today)
        elif date_range == "week":
            start_of_week = today - timedelta(days=today.weekday())
            bookings_list = bookings_list.filter(created_at__gte=start_of_week)
        elif date_range == "month":
            start_of_month = today.replace(day=1)
            bookings_list = bookings_list.filter(created_at__gte=start_of_month)
            
   
    ordered_bookings = bookings_list.order_by('-created_at')
    
    # --- Add Pagination ---
    paginator = Paginator(ordered_bookings, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    users_email_options = Booking.objects.values_list('user__email', flat=True).distinct()
    turf_names_options = Booking.objects.values_list('turf__turf_name', flat=True).distinct()
    
    context = {
        'bookings': page_obj, 
        'users_email': users_email_options,
        'turf_names': turf_names_options,
    }
    return render(request, '_bookings_admin.html', context)
