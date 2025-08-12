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
    bookings = user.bookings.all().order_by('-booking_date', '-start_time')
    now = timezone.now()

    past_bookings_list = []
    upcoming_bookings = []
    total_duration = timedelta()
    
    # --- NEW: Keep track of the IDs of past bookings ---
    past_booking_ids = []

    for booking in bookings:
        end_dt = timezone.make_aware(datetime.combine(booking.booking_date, booking.end_time))
        if booking.end_time < booking.start_time:
            end_dt += timedelta(days=1)
        
        if end_dt < now:
            past_bookings_list.append(booking)
            past_booking_ids.append(booking.id) # 👈 Add the ID to our new list
            
            start_dt = timezone.make_aware(datetime.combine(booking.booking_date, booking.start_time))
            duration = end_dt - start_dt
            total_duration += duration
        else:
            upcoming_bookings.append(booking)
            
    upcoming_bookings.reverse()
    
    # --- NEW: Create a QuerySet from the IDs we found ---
    past_bookings_queryset = user.bookings.filter(id__in=past_booking_ids)

    # --- Calculate statistics ---
    # (The rest of your statistics logic remains the same)
    completed_booking_count = len(past_bookings_list)
    hours_played = total_duration.total_seconds() / 3600
    total_cost = sum(b.total_cost for b in bookings if b.status != 'cancelled')
    most_booked_turfs = Turf.objects.filter(
        bookings__user=user, 
        bookings__status='confirmed'
    ).annotate(
        total_booking_count=Count('bookings')
    ).order_by('-total_booking_count')[:3]

    # --- Update the return dictionary ---
    return {
        'past_bookings': past_bookings_list, # The list for your template
        'past_bookings_queryset': past_bookings_queryset, # 👈 The QuerySet for your logic
        'upcoming_bookings': upcoming_bookings,
        'hours_played': f'{hours_played:.1f}',
        'total_cost': total_cost,
        'most_booked_turfs': most_booked_turfs,
        'upcoming_bookings_count': len(upcoming_bookings),
        'completed_booking_count': completed_booking_count
    }