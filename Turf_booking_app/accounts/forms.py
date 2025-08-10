from django.contrib.auth.forms import UserCreationForm
from .models import User, Turf
from django.core.exceptions import ValidationError
from django import forms


class CustomUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['fullname', 'email','phone', 'location', 'latitude',
                  'longitude']
        
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            digits_only = ''.join(filter(str.isdigit, phone))
            if len(digits_only) != 10:
                raise ValidationError("Phone number must have exactly 10 digits.")
            if not digits_only.isdigit():
                raise ValidationError("Phone number must contain only digits.")
            return digits_only
        else:
            raise ValidationError("Phone number is required.")


class TurfProfileForm(forms.ModelForm):
    class Meta:
        model = Turf
        fields = [
            'turf_name',
            'address',
            'district',
            'place',
            'city',
            'pincode',
            'opening_time',
            'closing_time',
            'contact_number',
            'cost_per_hour',
            'sports',
            'location',
            'latitude',
            'longitude'
        ]
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
            'sports': forms.CheckboxSelectMultiple(),
        }
