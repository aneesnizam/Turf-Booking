import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import Booking # <-- Make sure to import your Booking model

# Get a logger instance
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Finds and cancels pending bookings older than 30 minutes.'

    def handle(self, *args, **options):
        # 1. Define the time threshold: 30 minutes ago from now.
        time_threshold = timezone.now() - timedelta(minutes=30)
        
        # 2. Find all bookings that are 'pending' AND were created before the threshold.
        # We use created_at__lt which means "created_at is less than".
        bookings_to_cancel = Booking.objects.filter(
            status='pending',
            created_at__lt=time_threshold
        )
        
        # 3. Get the count of bookings that will be cancelled.
        count = bookings_to_cancel.count()
        
        if count > 0:
            # 4. Update their status to 'cancelled' in a single, efficient database query.
            bookings_to_cancel.update(status='cancelled')
            
            # 5. Log a success message to the console.
            self.stdout.write(self.style.SUCCESS(f'Successfully cancelled {count} pending bookings.'))
        else:
            # 6. Log a message if no bookings needed cancellation.
            self.stdout.write(self.style.NOTICE('No pending bookings to cancel.'))