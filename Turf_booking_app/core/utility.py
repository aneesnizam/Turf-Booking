from datetime import datetime, timedelta
from django.db.models import Q
from accounts.models import Booking

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
