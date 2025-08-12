from django.shortcuts import render, redirect
from .forms import CustomUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.conf import settings
import requests

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            messages.success(request, "login successfull")
            return redirect('home')
        else:
            messages.error(request, "Invalid Credentials")
            return render(request, 'user_login.html')

    return render(request, 'user_login.html')


def admin_login(request):
    return render(request, 'admin_login.html')


def user_register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = CustomUserForm(request.POST)
        try:
            if form.is_valid():
                user = form.save(commit=False)

                user_type = request.POST.get('user_type', 'user')
                user.role = 'owner' if user_type == 'owner' else 'user'
                
                user.save()
                
                messages.success(request, "Registered Successfully")
                return redirect('user_login')
        except Exception as e:
            print("Registration error:", e)
            messages.error(request, "A server error occurred. Please try again later.")
        
        return render(request, 'user_register.html', {'form': form})

    form = CustomUserForm()
    return render(request, 'user_register.html', {'form': form})


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'landing.html')


def explore_sports(request):
    return render(request, 'explore_sports.html')


def forgot_password(request):
    return render(request, 'forgot_password.html')


def autocomplete_place(request):
    query = request.GET.get("q")
    if not query:
        return JsonResponse([], safe=False)

    try:
        api_key = settings.LOCATIONIQ_API_KEY
        url = "https://api.locationiq.com/v1/autocomplete"
        params = {
            "key": api_key,
            "q": query,
            "format": "json",
            "countrycodes": "in",
            "viewbox": "76.0,12.8,77.6,8.1",
            "bounded": 1,
            "limit": 5,
            "addressdetails": 1
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        suggestions = []
        for item in data:
            address = item.get('address', {})
            
            city_name = address.get('town') or address.get('city', '')
            state_district = address.get('state_district', '')
            county = address.get('county', '')
            final_district = state_district or county or ""
           
            
            locality = address.get('suburb') or address.get('village') or address.get('city_district') or address.get('name', '')
            
            
            suggestions.append({
                'display_name': item.get('display_name'),
                'place': locality,
                'city': city_name,
                'district': final_district,
                'pincode': address.get('postcode', ''),
                'latitude': item.get('lat'),  
                'longitude': item.get('lon')
            })

        return JsonResponse(suggestions, safe=False)

    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return JsonResponse({"error": "Failed to fetch location data"}, status=500)
    except Exception as e:
        print(f"Autocomplete error: {e}")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)


# -------------------- STATIC PAGES --------------------
def about_us(request):
    return render(request,'pages/about_us.html')


def contact_us(request):
    return render(request,'pages/contact_us.html')


def privacy_policy(request):
    return render(request,'pages/privacy_policy.html')


def terms_and_conditions(request):
    return render(request,'pages/terms_and_conditions.html')


def cancellation_policy(request):
    return render(request, 'pages/cancellation_policy.html')
