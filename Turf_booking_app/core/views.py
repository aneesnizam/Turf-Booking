from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required , user_passes_test
from django.db import transaction
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model
from accounts.models import Turf, TurfImage, Sport,Booking,Rating
from accounts.forms import TurfProfileForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string,get_template
from django.shortcuts import get_object_or_404
User = get_user_model()
import json
from django.http import JsonResponse ,HttpResponse,HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import F, Q, Case, When, Value, IntegerField ,Count,Avg ,OuterRef, Subquery, ExpressionWrapper, fields,Sum
from haversine import haversine,Unit
from datetime import datetime, timedelta
from django.utils import timezone 
from decimal import Decimal, InvalidOperation
from django.db.models.functions import Coalesce
from xhtml2pdf import pisa
import io
import qrcode 
from .utility import get_booking_details
from .models import Achievement,UserAchievement
from .achievements_logic import check_all_achievements



@login_required
def logoutuser(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('landing')



@login_required
@require_POST
def delete_review(request,review_id):
    review = get_object_or_404(Rating,id = review_id)
    if request.user == review.user or request.user.is_staff:
        review.delete()
        return JsonResponse({'success':True})
    return HttpResponseForbidden('You are not allowed to delete this review.')
    
    
    
    
# -------------------- HOME --------------------
@login_required
def home(request):
    all_turfs = Turf.objects.all().filter(status = 'active', verification_status='verified')
    top_rated_turfs = all_turfs.annotate(average_ratings = Coalesce(Avg('ratings__score'),0.0)).order_by('-average_ratings')[:3]
    context = {
        'all_turfs':top_rated_turfs,
        'turf_counts': all_turfs.count()
    }
    return render(request, 'home.html',context)







# -------------------- TOGGLE - FAVORITES --------------------
@login_required
def toggle_favourite(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    if turf in request.user.favourites.all():
        request.user.favourites.remove(turf)
    else:
        request.user.favourites.add(turf)
    return redirect(request.META.get('HTTP_REFERER', 'home'))



# -------------------- TURFS LIST --------------------
@login_required
def turfs(request):
    # --- 1. Initial Setup & User Location ---
    base_turfs_qs = Turf.objects.filter(
        status='active', 
        verification_status='verified'
    ).prefetch_related('images', 'sports').annotate(
        avg_score=Coalesce(Avg('ratings__score'), 0.0)
    )
    user_latitude = getattr(request.user, 'latitude', None)
    user_longitude = getattr(request.user, 'longitude', None)

    # --- 2. Identify "Nearby" Turfs ---
    nearby_turfs_qs = Turf.objects.none()
    nearby_turf_ids = set()
    if user_latitude and user_longitude:
        lat_range, lon_range = 0.15, 0.15 # Approx 16.7km radius
        nearby_turfs_qs = base_turfs_qs.filter(
            latitude__gte=user_latitude - lat_range, latitude__lte=user_latitude + lat_range,
            longitude__gte=user_longitude - lon_range, longitude__lte=user_longitude + lon_range
        )
        nearby_turf_ids = set(nearby_turfs_qs.values_list('id', flat=True))

    # --- 3. Apply Search Filters ---
    filtered_turfs_qs = base_turfs_qs
    location_query = request.GET.get('location', '').strip()
    sports_query = request.GET.getlist('sports[]') 
    start_time_query = request.GET.get('start_time')
    end_time_query = request.GET.get('end_time')
    if location_query:
        filtered_turfs_qs = filtered_turfs_qs.filter(
            Q(city__icontains=location_query) |
            Q(place__icontains=location_query) |
            Q(district__icontains=location_query)
        )
    if sports_query:
        filtered_turfs_qs = filtered_turfs_qs.filter(sports__name__in=sports_query).distinct()
    if start_time_query and end_time_query:
        filtered_turfs_qs = filtered_turfs_qs.filter(
            opening_time__lte=start_time_query,
            closing_time__gte=end_time_query
        )

    # --- 4. Apply Sorting ---
    sort_option = request.GET.get('sort')
    if sort_option == 'price_low':
        ordered_turfs = filtered_turfs_qs.order_by('cost_per_hour')
    elif sort_option == 'price_high':
        ordered_turfs = filtered_turfs_qs.order_by('-cost_per_hour')
    elif sort_option == 'rating_high':
        ordered_turfs = filtered_turfs_qs.order_by(F('avg_score').desc(nulls_last=True))
    else:
        ordered_turfs = filtered_turfs_qs.annotate(
            is_nearby=Case(
                When(id__in=nearby_turf_ids, then=Value(1)), #
                default=Value(2),                          
                output_field=IntegerField()
            )
        ).order_by('is_nearby', '-avg_score') 

    # --- 5. Pagination ---
    paginator = Paginator(ordered_turfs, 9) 
    page_number = request.GET.get('page', 1)
    turfs_page = paginator.get_page(page_number)

    # --- 6. Calculate Distance (Only for Nearby Turfs on the Current Page) ---
    if user_latitude and user_longitude:
        user_location = (float(user_latitude), float(user_longitude))
        for turf in turfs_page:
            
            if turf.id in nearby_turf_ids:
                turf_location = (float(turf.latitude), float(turf.longitude))
                distance = haversine(user_location, turf_location, unit=Unit.KILOMETERS)
                turf.distance = round(distance, 2)
            else:
                turf.distance = None 

    # --- 7. Prepare Context & Final Response ---
    context = {
        'all_turfs': turfs_page, 
        'turf_counts': paginator.count,
        'all_sports': Sport.objects.all(),
        'selected_sports': sports_query,
        'latitude': user_latitude,
        'longitude': user_longitude,
        'turfs_to_display': nearby_turfs_qs,  
    }
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if is_ajax:
        html = render_to_string('core_base/partials/_turf_card_list.html', context, request=request)
        return JsonResponse({'html': html, 'has_next': turfs_page.has_next()})
    return render(request, 'turfs.html', context)



# -------------------- UPDATE PROFILE --------------------
@login_required
def update_profile(request):
    # --- 1. Setup ---
    user = request.user

    if request.method == 'POST':
        # --- 2. Process Form Data ---
        new_fullname = request.POST.get('fullname', user.fullname).strip()
        new_phone = request.POST.get('phone', user.phone).strip()
        profile_picture_file = request.FILES.get('profile_picture')
        clear_profile_picture = 'profile_picture-clear' in request.POST

        try:
            with transaction.atomic():
                # --- 3. Update Text Fields ---
                user.fullname = new_fullname
                user.phone = new_phone
                
                # --- 4. Handle Profile Picture Update ---
                if (profile_picture_file or clear_profile_picture) and user.profile_picture:
                    if default_storage.exists(user.profile_picture.path):
                        default_storage.delete(user.profile_picture.path)

                if profile_picture_file:
                    user.profile_picture = profile_picture_file
                elif clear_profile_picture:
                    user.profile_picture = None

                # --- 5. Save Changes to Database ---
                fields_to_update = ['fullname', 'phone', 'profile_picture']
                user.save(update_fields=fields_to_update)

                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')

        except Exception as e:
            messages.error(request, f'Failed to update profile due to an unexpected error: {e}.')
            return redirect('profile')

    # --- 6. Handle GET Request ---
    return render(request, 'profile.html')



# -------------------- UPDATE PASSWORD --------------------
@login_required
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_password')

        if not current_password or not new_password or not confirm_new_password:
            messages.error(request, 'All password fields are required.')
            return render(request, 'profile.html')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('profile')

        if new_password != confirm_new_password:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'profile.html')

        if len(new_password) < 8:
            messages.error(
                request, 'New password must be at least 8 characters long.')
            return render(request, 'profile.html')

        try:
            with transaction.atomic():
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)

            messages.success(
                request, 'Your password has been changed successfully!')
            return redirect('profile')

        except Exception as e:
            messages.error(
                request, 'An unexpected error occurred while changing your password. Please try again.')
            return render(request, 'profile.html')

    return render(request, 'profile.html')



# -------------------- TURF REGISTER --------------------
@login_required
def turf_register(request):
    # --- 1. Authorization & Initial Setup ---
    user = request.user
    if not user.is_owner:
        messages.error(request, "Only turf owners can register turfs.")
        return redirect('home')

    all_sports = Sport.objects.all()

    # --- 2. Handle Form Submission (POST Request) ---
    if request.method == 'POST':
        form = TurfProfileForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')[:3] 

        if form.is_valid():
            try:
                # --- 3. Save to Database within a Transaction ---
                with transaction.atomic():
                    turf = form.save(commit=False)
                    turf.owner = user
                    turf.verification_status = 'pending'
                    turf.status = 'active'
                    turf.save()

                    sport_ids = request.POST.getlist('sports')
                    sport_objects = Sport.objects.filter(id__in=sport_ids)
                    turf.sports.set(sport_objects)

                    for image in images:
                        TurfImage.objects.create(turf=turf, image=image)

                messages.success(request, "Turf submitted for verification.")
                return redirect('turf_register')
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")

        else:
            # --- 4. Handle Invalid Form ---
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
        
        # If there was an error, re-render the page with the submitted data
        context = {'form': form, 'all_sports': all_sports}
        return render(request, 'turf_register.html', context)

    # --- 5. Handle Initial Page Load (GET Request) ---
    else:
        form = TurfProfileForm()
        context = {'form': form, 'all_sports': all_sports}
        return render(request, 'turf_register.html', context)



# -------------------- UPDATE USER LOCATION (AJAX) --------------------
@login_required 
@require_POST 
def update_user_location(request):
    
    try:
        # 1. Load the data from the incoming JSON request body.
        data = json.loads(request.body)
        lat = data.get('lat')
        lng = data.get('lng')

        # 2. Check if latitude and longitude are provided.
        if lat is not None and lng is not None:
            # 3. Get the current user object.
            user = request.user
            
            # 4. Update the fields on the user model.
            
            user.latitude = lat
            user.longitude = lng
            
            # 5. Save the changes to the database.
            user.save(update_fields=['latitude', 'longitude'])
            
            # 6. Return a success response.
            return JsonResponse({'status': 'success', 'message': 'Location updated successfully.'})
        else:
            # Return an error if data is missing.
            return JsonResponse({'status': 'error', 'message': 'Missing latitude or longitude.'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

# -------------------- FAVORITES  --------------------    
@login_required    
def favorites(request):
    user_favorites = request.user.favourites.all()
    user_input = request.GET.get('q','').strip()
    if user_input:
        user_favorites = user_favorites.filter(Q(city__icontains = user_input)| Q(place__icontains = user_input)|Q(turf_name__icontains = user_input))
    context = {
        'favorites':user_favorites,
    }
    return render(request,'favorites.html',context)
        
        

# -------------------- CHECK AVAILABILITY (AJAX) --------------------
@login_required
def check_availability(request, turf_id):
    # --- 1. Get and Validate Parameters ---
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date not provided'}, status=400)
    
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        turf = get_object_or_404(Turf, id=turf_id)
    except (ValueError, Turf.DoesNotExist):
        return JsonResponse({'error': 'Invalid date or turf ID.'}, status=400)

    # --- 2. Check Booking Window Limit ---
    today = timezone.localdate()
    date_limit = today + timedelta(days=20)
    if selected_date > date_limit:
        return JsonResponse({'available_slots': [], 'message': 'You cannot book more than 20 days in advance.'})
    
    # --- 3. Get All Conflicting Bookings ---
    next_day = selected_date + timedelta(days=1)
    conflicting_bookings = Booking.objects.filter(
        turf=turf, 
        booking_date__in=[selected_date, next_day]
    ).exclude(status='cancelled')

    booked_ranges = []
    for booking in conflicting_bookings:
        start_dt = timezone.make_aware(datetime.combine(booking.booking_date, booking.start_time))
        end_dt = timezone.make_aware(datetime.combine(booking.booking_date, booking.end_time))
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        booked_ranges.append((start_dt, end_dt))

    # --- 4. Generate and Filter Time Slots ---
    available_slots = []
    op_start_dt = timezone.make_aware(datetime.combine(selected_date, turf.opening_time))
    op_end_dt = timezone.make_aware(datetime.combine(selected_date, turf.closing_time))
    
    if turf.closing_time < turf.opening_time:
        op_end_dt += timedelta(days=1)
    
    now = timezone.localtime(timezone.now())
    current_slot_dt = op_start_dt

    while current_slot_dt < op_end_dt:
        if current_slot_dt < now:
            current_slot_dt += timedelta(minutes=30)
            continue

        slot_is_available = not any(start <= current_slot_dt < end for start, end in booked_ranges)
        
        if slot_is_available:
            available_slots.append(current_slot_dt.strftime('%H:%M'))
            
        current_slot_dt += timedelta(minutes=30)
        
    return JsonResponse({'available_slots': available_slots})



# -------------------- TURF DETAILS & BOOKING CREATION --------------------
@login_required
def turf_details(request, turf_id):
    # --- 1. Initial Setup ---
    turf = get_object_or_404(Turf, id=turf_id)
    ratings = turf.ratings.all().annotate(
            is_my_review=Case(
                When(user=request.user , then=Value(1)),
                     default=Value(0),
                     output_field=IntegerField()
            )
        ).order_by('-is_my_review','-created_at')



    if request.method == 'POST':
        # --- 2. Process and Validate Form Data ---
        date_str = request.POST.get('booking_date')
        start_time_str = request.POST.get('start_time')
        duration_str = request.POST.get('duration')

        if not all([date_str, start_time_str, duration_str]):
            messages.error(request, 'Missing form data. Please fill all fields.')
            return redirect('turf_details', turf_id=turf.id)
        
        try:
            duration_hours = Decimal(duration_str)
            booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
        except (InvalidOperation, TypeError, ValueError):
            messages.error(request, "Invalid form data submitted.")
            return redirect('turf_details', turf_id=turf.id)

        # --- 3. Calculate Booking Times and Perform Checks ---
        start_datetime = timezone.make_aware(datetime.combine(booking_date, start_time_obj))
        end_datetime = start_datetime + timedelta(hours=float(duration_hours))
        
        if start_datetime <= timezone.now():
            messages.error(request, 'Sorry, you cannot book a time in the past.')
            return redirect('turf_details', turf_id=turf.id)

        # --- 4. Correct Concurrency Check ---
        conflicting_bookings = Booking.objects.filter(
            turf=turf,
            booking_date=start_datetime.date(),
            start_time__lt=end_datetime.time(),
            end_time__gt=start_datetime.time()
        ).exclude(status='cancelled')
        
        if conflicting_bookings.exists():
            messages.error(request, 'Sorry, this time slot was just booked. Please select another time.')
            return redirect('turf_details', turf_id=turf.id)
        
        
            

        # --- 5. Create and Save the Booking ---
        total_cost = (Decimal(turf.cost_per_hour) * duration_hours)
        try:
            with transaction.atomic():
                booking = Booking.objects.create(
                    user=request.user,
                    turf=turf,
                    booking_date=start_datetime.date(),
                    start_time=start_datetime.time(),
                    end_time=end_datetime.time(),
                    total_cost=total_cost,
                    status='confirmed'
                )
            
            messages.success(request, f'Successfully booked {turf.turf_name}!')
            return redirect('view_booking_detail', booking_token=booking.verify_token)

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('turf_details', turf_id=turf.id)
            
    # --- 6. Handle GET Request ---
    context = {
        'turf_detail': turf,
        'total_bookings': turf.bookings.count(),
        'current_hour': datetime.now().hour,
        'ratings': ratings,
    }
    return render(request, 'turf_details.html', context)



# -------------------- BOOKINGS --------------------
def booking(request):
    # --- 1. Get all booking data from the helper function ---
    booking_data = get_booking_details(request.user)

  
    paginator = Paginator(booking_data['past_bookings'], 5) 
    completed_page_obj = paginator.get_page(request.GET.get('completed_page'))
    
    # --- 3. Handle AJAX requests (if any) ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'partials/completed_bookings.html', {
            'completed_page_obj': completed_page_obj
        })

    # --- 4. Prepare the context and render the full page ---
    context = {
        'completed_page_obj': completed_page_obj,
        'upcoming_bookings': booking_data['upcoming_bookings'],
        'hours_played': booking_data['hours_played'],
        'total_cost': booking_data['total_cost'],
        'most_booked_turfs': booking_data['most_booked_turfs'],
        'upcoming_bookings_count': booking_data['upcoming_bookings_count'],
        'completed_booking_count': booking_data['completed_booking_count']
    }
    return render(request, 'booking.html', context)



# -------------------- SUBMIT RATING (AJAX) --------------------
@login_required
@require_POST
def submit_rating(request):
    # --- 1. Process Incoming Data ---
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        score = int(data.get('score'))
        comment = data.get('comment', '')

        # --- 2. Validate the Booking ---
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        if Rating.objects.filter(booking=booking).exists():
            return JsonResponse({'status': 'error', 'message': 'You have already rated this booking.'}, status=400)

        # --- 3. Create the Rating ---
        Rating.objects.create(
            user=request.user,
            turf=booking.turf,
            booking=booking,
            score=score,
            comment=comment
        )
        
        return JsonResponse({'status': 'success', 'message': 'Thank you for your rating!'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    

# -------------------- VIEW BOOKING DETAIL --------------------    
@login_required
def view_booking_detail(request, booking_token):
    # --- 1. Get Booking Details ---
    booking_details = get_object_or_404(Booking, verify_token=booking_token)
    
    # --- 2. Calculate Duration Correctly ---
    start_dt = datetime.combine(booking_details.booking_date, booking_details.start_time)
    end_dt = datetime.combine(booking_details.booking_date, booking_details.end_time)

    # Handle overnight case
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
        
    duration_delta = end_dt - start_dt
    
    # --- 3. Format Duration for Display ---
    total_minutes = duration_delta.total_seconds() / 60
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    
    if hours > 0 and minutes > 0:
        duration_str = f"{hours} hour{'s' if hours > 1 else ''}, {minutes} minutes"
    elif hours > 0:
        duration_str = f"{hours} hour{'s' if hours > 1 else ''}"
    else:
        duration_str = f"{minutes} minutes"

    # --- 4. Prepare Context and Render ---
    context = {
        'booking': booking_details,
        'duration': duration_str,
    }
    return render(request,'view_booking_detail.html', context)



# -------------------- GENERATE INVOICE PDF --------------------
@login_required
def generate_invoice_pdf(request, booking_id):
    # --- 1. Get Booking and Verify User ---
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # --- 2. Calculate Duration Correctly ---
    start_dt = datetime.combine(booking.booking_date, booking.start_time)
    end_dt = datetime.combine(booking.booking_date, booking.end_time)

    if end_dt < start_dt:
        end_dt += timedelta(days=1)
        
    duration_delta = end_dt - start_dt
    hours = duration_delta.total_seconds() / 3600
    
    # --- 3. Render HTML Template ---
    template_path = 'pages/invoice_template.html'
    context = {
        'booking': booking,
        'duration': round(hours, 2)
    }
    template = get_template(template_path)
    html = template.render(context)
    
    # --- 4. Create and Return PDF Response ---
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{booking.id}.pdf"'

    pisa_status = pisa.CreatePDF(
        io.StringIO(html),
        dest=response,
        encoding='UTF-8'
    )

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response



# -------------------- BOOKING QR CODE --------------------
@login_required(login_url='user_login')
def booking_qr(request, booking_token):
    
    # --- 1. Get Booking and Verify User ---
    booking = get_object_or_404(Booking, verify_token=booking_token, user=request.user)
    
    # --- 2. Correctly Build the URL ---
    booking_url = request.build_absolute_uri(f"/view_booking_detail/{booking.verify_token}")
    
    # --- 3. Generate QR Code Image ---
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(booking_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # --- 4. Prepare and Return Image Response ---
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return HttpResponse(buffer, content_type="image/png")



# -------------------- CANCEL BOOKING --------------------
@login_required
def cancel_booking(request,booking_id):
    user = request.user
    booking = Booking.objects.get(id = booking_id)
    if booking.user == user:
        booking.delete()
    return redirect('booking')



# -------------------- DASHBOARD REDIRECT --------------------
@login_required
def dashboard_redirect_view(request):
    user = request.user
    if user.role == 'owner':
        # Check if the user has at least one verified turf
        if user.turfs.filter(verification_status='verified').exists():
            return redirect('owner_dashboard')
        else:
            messages.info(
                request, "Please register and verify at least one turf to access your dashboard. ")
            return redirect('turf_register')  # No verified turf yet
    return redirect('home')  # Non-turf owners



# -------------------- PROFILE --------------------
@login_required
def profile(request):
    booking_data = get_booking_details(request.user)
    favourites_count = request.user.favourites.count()
    total_count = booking_data['completed_booking_count'] + booking_data['upcoming_bookings_count']
    check_all_achievements(request.user)
    
    
    
    # --- Achievement Data Fetching ---
    user_progress = UserAchievement.objects.filter(
        user=request.user, 
        achievement=OuterRef('pk')
    )

    # Get all achievements and annotate them with the user's specific progress
    achievements = Achievement.objects.annotate(
        current_progress=Subquery(user_progress.values('current_progress')[:1]),
        unlocked=Subquery(user_progress.values('unlocked')[:1]),
        # Calculate progress percentage for the progress bar
        progress_percentage=ExpressionWrapper(
            100.0 * F('current_progress') / F('target_value'),
            output_field=fields.FloatField()
        )
    ).order_by('-unlocked', '-progress_percentage') # Show unlocked and in-progress first
    
    achievement_unlocked_count = achievements.filter(unlocked=True).count()
    
    context = {
        'upcoming_bookings': booking_data['upcoming_bookings'][:4],
        'hours_played': booking_data['hours_played'],
        'total_cost': booking_data['total_cost'],
        'past_bookings':booking_data['past_bookings'][:4],
        'most_booked_turfs': booking_data['most_booked_turfs'],
        'upcoming_bookings_count': booking_data['upcoming_bookings_count'],
        'completed_booking_count': booking_data['completed_booking_count'],
        'favourites_count' : favourites_count,
        'total_count' : total_count,
        'achievements' : achievements,
        'achievement_unlocked_count':achievement_unlocked_count
    }
    
    return render(request, 'profile.html',context)


def profile_settings(request):
    user = request.user

    if request.method == "POST":
        user.location = request.POST.get("location", "")
        user.latitude = request.POST.get("latitude", "")
        user.longitude = request.POST.get("longitude", "")
        user.booking_updates = "booking_updates" in request.POST
        user.new_turfs_alerts = "new_turfs" in request.POST
        user.save()

        messages.success(request, "Preferences updated successfully.")
        return redirect("profile")  

    return redirect('profile')



# -------------------- OWNER DASHBOARD --------------------
@login_required
@user_passes_test(lambda u:u.role == 'owner')
def owner_dashboard(request):
    active_turfs = request.user.turfs
    active_counts = active_turfs.count()
    active_turfs = active_turfs.annotate(total = Sum('bookings__total_cost')).order_by('-total')
    
    
    context = {
        'active_counts': active_counts,
        'turfs' : active_turfs
    }
    return render(request, 'owner_dashboard.html', context)



def recent_bookings(request):
    return render(request,'recent_bookings.html')


def delete_turf(request,turf_id):
    turf = Turf.objects.get(id = turf_id,owner = request.user)
    if turf:
        turf.delete()
    return redirect('owner_dashboard')
    