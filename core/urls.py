from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('hr/signup/', views.hr_signup, name='hr_signup'),
    path('hr/login/', views.hr_login, name='hr_login'),
    path('candidate/signup/', views.candidate_signup, name='candidate_signup'),
    path('candidate/login/', views.candidate_login, name='candidate_login'),
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('candidate/dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('hr/create-assessment/', views.create_assessment, name='create_assessment'),
    path('hr/view-assessments/', views.view_assessments, name='view_assessments'),
]