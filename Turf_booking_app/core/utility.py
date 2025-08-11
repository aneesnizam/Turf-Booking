from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from accounts.models import Booking
from django.db.models import Count
from accounts.models import Turf 


def generate_slots(open_time, close_time):
    slots = []
    current = datetime.combine(datetime.today(), open_time)
    end = datetime.combine(datetime.today(), close_time)
    while current + timedelta(minutes=30) <= end:
        slot = (current.time(), (current + timedelta(minutes=30)).time())
        slots.append(slot)
        current += timedelta(minutes=30)
    return slots



def get_booked_slots(turf, date):
    bookings = Booking.objects.filter(turf=turf, date=date)
    return [(b.start_time, b.end_time) for b in bookings]



def get_booking_details(user):
  
    # --- 1. Fetch all bookings for the user ---
    bookings = user.bookings.all().order_by('-booking_date', '-start_time')
    now = timezone.now()

    # --- 2. Classify bookings and calculate duration ---
    past_bookings = []
    upcoming_bookings = []
    total_duration = timedelta()

    for booking in bookings:
        # Combine date and time to create a full datetime object
        end_dt = timezone.make_aware(datetime.combine(booking.booking_date, booking.end_time))

        # Handle bookings that cross midnight
        if booking.end_time < booking.start_time:
            end_dt += timedelta(days=1)
        
        # Check if the booking has already finished
        if end_dt < now:
            past_bookings.append(booking)
            # Calculate duration for past bookings
            start_dt = timezone.make_aware(datetime.combine(booking.booking_date, booking.start_time))
            duration = end_dt - start_dt
            total_duration += duration
        else:
            upcoming_bookings.append(booking)
    upcoming_bookings.reverse()        
    # --- 3. Calculate statistics ---
    completed_booking_count = len(past_bookings)
    hours_played = total_duration.total_seconds() / 3600
    total_cost = sum(b.total_cost for b in bookings if b.status != 'cancelled')

    most_booked_turfs = Turf.objects.filter(
        bookings__user=user, 
        bookings__status='confirmed'
    ).annotate(
        total_booking_count=Count('bookings')
    ).order_by('-total_booking_count')[:3]

    # --- 4. Return all calculated data in a dictionary ---
    return {
        'past_bookings': past_bookings,
        'upcoming_bookings': upcoming_bookings,
        'hours_played': f'{hours_played:.1f}',
        'total_cost': total_cost,
        'most_booked_turfs': most_booked_turfs,
        'upcoming_bookings_count': len(upcoming_bookings),
        'completed_booking_count': completed_booking_count
    }
