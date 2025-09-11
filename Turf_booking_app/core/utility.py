from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
from accounts.models import Booking
from django.db.models import Count
from accounts.models import Turf,TurfImage,Rating 
from django.db.models import Prefetch


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
    # Base bookings query optimized
    bookings = (
        user.bookings.all()
        .select_related("turf")  # avoids repeated turf queries
        .prefetch_related(
            Prefetch(
                "turf__images",  # fetch all turf images in one go
                queryset=TurfImage.objects.order_by("id")
            ),
            "turf__ratings"  # preload ratings if needed in template
        )
        .order_by('-booking_date', '-start_time')
    )

    now = timezone.now()
    past_bookings_list, upcoming_bookings, cancelled_bookings = [], [], []
    total_duration = timedelta()
    past_booking_ids = []

    for booking in bookings:
        end_dt = timezone.make_aware(datetime.combine(booking.booking_date, booking.end_time))
        if booking.end_time < booking.start_time:
            end_dt += timedelta(days=1)

        if booking.status == "cancelled":
            cancelled_bookings.append(booking)
            continue

        if end_dt < now:
            past_bookings_list.append(booking)
            past_booking_ids.append(booking.id)
            start_dt = timezone.make_aware(datetime.combine(booking.booking_date, booking.start_time))
            duration = end_dt - start_dt
            total_duration += duration
        else:
            if booking.status in ["confirmed", "pending"]:
                upcoming_bookings.append(booking)

    upcoming_bookings.sort(key=lambda b: (b.booking_date, b.start_time))

    past_bookings_queryset = user.bookings.filter(id__in=past_booking_ids)

    completed_booking_count = len(past_bookings_list)
    hours_played = total_duration.total_seconds() / 3600
    total_cost = sum(b.total_cost for b in bookings if b.status != 'cancelled')

    most_booked_turfs = (
        Turf.objects.filter(bookings__user=user, bookings__status='confirmed')
        .annotate(total_booking_count=Count('bookings'))
        .prefetch_related(
            Prefetch("images", queryset=TurfImage.objects.order_by("id"))
        )
        .order_by('-total_booking_count')[:3]
    )

    return {
        'past_bookings': past_bookings_list,
        'past_bookings_queryset': past_bookings_queryset,
        'cancelled_bookings': cancelled_bookings,
        'upcoming_bookings': upcoming_bookings,
        'hours_played': f'{hours_played:.1f}',
        'total_cost': total_cost,
        'most_booked_turfs': most_booked_turfs,
        'upcoming_bookings_count': len(upcoming_bookings),
        'completed_booking_count': completed_booking_count
    }