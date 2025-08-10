from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from datetime import date, timedelta
from decimal import Decimal
import uuid


class Manager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


    
class User(AbstractBaseUser, PermissionsMixin):
    fullname = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=200,default='',blank=True)
    favourites = models.ManyToManyField('Turf', related_name='fav_users', blank=True)

    ROLE_CHOICES = [
        ('user', 'Regular User'),
        ('owner', 'Turf Owner'),
        ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    objects = Manager()
    joined = models.DateField(auto_now_add=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']


    def __str__(self):
        return self.email
    
    
    @property
    def is_owner(self):
        return self.role == 'owner'


class Sport(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    

    
class Turf(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('closed', 'Closed'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='turfs')
    turf_name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    contact_number = models.CharField(max_length=15)
    cost_per_hour = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    verification_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('declined', 'Declined')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sports = models.ManyToManyField(Sport, related_name='turfs')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=200,default='',blank=True)
    
    @property
    def average_rating(self):
        return round(self.ratings.aggregate(avg =models.Avg("score"))['avg'] or 0.0,1)
    
  
 
    def __str__(self):
        return self.turf_name



class TurfImage(models.Model):
    turf = models.ForeignKey(Turf, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='turf_images/')

    def __str__(self):
        return f"Image for {self.turf.turf_name}"




def generate_token():
    return uuid.uuid4().hex 

class Booking(models.Model):
    
    
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    verify_token = models.CharField(max_length=36, default=generate_token, unique=True)


    

        
    
    @property
    def human_date(self):
        if not self.booking_date:
            return ""
        today = date.today()
        if self.booking_date == today:
            return "Today"
        elif self.booking_date == today - timedelta(days=1):
            return "Yesterday"
        elif self.booking_date == today + timedelta(days=1):
            return "Tomorrow"
        else:
            return self.booking_date.strftime("%a, %b %d") 

    def __str__(self):
        return f"Booking for {self.turf.turf_name} by {self.user.email} on {self.booking_date}"

    class Meta:
        unique_together = ('turf', 'booking_date', 'start_time')
        
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name="ratings")
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="ratings")
    score = models.IntegerField(default=0) # e.g., 1 to 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return f"{self.turf.turf_name} - {self.score} stars"