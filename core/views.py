from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

# Placeholder views for now
def hr_signup(request):
    return render(request, 'home.html')  # Temporary redirect

def hr_login(request):
    return render(request, 'home.html')

def candidate_signup(request):
    return render(request, 'home.html')

def candidate_login(request):
    return render(request, 'home.html')