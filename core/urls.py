from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('hr/signup/', views.hr_signup, name='hr_signup'),
    path('hr/login/', views.hr_login, name='hr_login'),
    path('candidate/signup/', views.candidate_signup, name='candidate_signup'),
    path('candidate/login/', views.candidate_login, name='candidate_login'),
]