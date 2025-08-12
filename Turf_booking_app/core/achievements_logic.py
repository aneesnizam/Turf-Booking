from django.utils import timezone
from django.db.models import Count ,Sum,F
from .models import Achievement,UserAchievement
from .utility import get_booking_details


def update_achievement_progress(user,slug,progress):
    try:
        achievement = Achievement.objects.get(slug=slug)
        user_ach, created = UserAchievement.objects.get_or_create(achievement=achievement,user=user)
        if not user_ach.unlocked:
            user_ach.current_progress = progress
            if user_ach.current_progress >= achievement.target_value:
                user_ach.unlocked = True
                user_ach.unlocked_at = timezone.now()
            user_ach.save()
    except Achievement.DoesNotExist:
        pass
    
    
def check_all_achievements(user):
    
  
    booking_data = get_booking_details(user)

    # 1. First Timer & Night Owl (simple checks)
    completed_bookings = booking_data['past_bookings_queryset']
    if completed_bookings.count() > 0:
        
        
        update_achievement_progress(user,'first-timer',1)
    
    if completed_bookings.filter(start_time__hour__gte=22).exists(): # 10 PM or later
        update_achievement_progress(user, 'night-owl', 1)

    # 2. Loyalist (book same turf 5 times)
    most_booked_turf = completed_bookings.values('turf').annotate(count=Count('turf')).order_by('-count').first()
    if most_booked_turf:
        update_achievement_progress(user, 'loyalist', most_booked_turf['count'])
        
    # 3. Turf Explorer (book 5 different turfs)
    distinct_turfs = completed_bookings.values('turf').distinct().count()
    update_achievement_progress(user, 'turf-explorer', distinct_turfs)

    # 4. Big Spender (spend over 10000)
    total_spent = completed_bookings.aggregate(total=Sum('total_cost'))['total'] or 0
    update_achievement_progress(user, 'big-spender', total_spent)
    
    # 5. Hat-trick Hero (book 3 times in a month)
    # This logic is more complex, but a simple version could be:
    # Find the month with the most bookings
    bookings_per_month = completed_bookings.annotate(month=F('booking_date__month'), year=F('booking_date__year')).values('month', 'year').annotate(count=Count('id')).order_by('-count').first()
    if bookings_per_month:
        update_achievement_progress(user, 'hat-trick-hero', bookings_per_month['count'])
        
      # 6. Early Bird (book before 9 AM)
   
    if completed_bookings.filter(start_time__hour__lt=9).exists():
        update_achievement_progress(user, 'early-bird', 1)

    # 7. Weekend Warrior (book 5 times on a weekend)
    # Filters for bookings where the 'weekday' is Saturday (7) or Sunday (1).
    # Note: Django's __week_day filter is 1=Sunday, 7=Saturday.
    weekend_bookings_count = completed_bookings.filter(booking_date__week_day__in=[1, 7]).count()
    update_achievement_progress(user, 'weekend-warrior', weekend_bookings_count)

 

    # 8. Social Star (rate 3 turfs)
    # This requires a Rating model linked to the user.
    # Let's assume you have a model like: user.ratings.all()
    if hasattr(user, 'ratings'): # Checks if the user model has a 'ratings' relationship
        ratings_count = user.ratings.count()
        update_achievement_progress(user, 'social-star', ratings_count)
    
        