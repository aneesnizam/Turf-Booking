from django.db import models
 
from django.conf import settings


# Create your models 
class Achievement(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,help_text="Unique key like 'first-timer'")
    description = models.CharField(max_length=225)
    icon_class = models.CharField(max_length=50, help_text="e.g., 'fas fa-trophy'")
    icon_color_class = models.CharField(max_length=50,help_text="e.g., 'text-yellow-400'")
    target_value  = models.PositiveIntegerField(default=1,help_text="Value needed to unlock (e.g., 5 bookings)")
    
    def __str__(self):
        return self.title
    
class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name= 'achievements')
    achievement = models.ForeignKey(Achievement,on_delete=models.CASCADE)
    current_progress = models.PositiveIntegerField(default=0)
    unlocked = models.BooleanField(default=False)
    unlocked_at  = models.DateTimeField(null=True,blank=True)
    
    class Meta:
        unique_together  = ('user','achievement')
        
    def __str__(self):
        return f'{self.user.fullname} - {self.achievement.title} ({'Unlocked' if self.unlocked else 'Locked'})'