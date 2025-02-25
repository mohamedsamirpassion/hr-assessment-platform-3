from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'core'  # Ensure this is present for namespace

urlpatterns = [
    path('', views.home, name='home'),
    path('hr/signup/', views.hr_signup, name='hr_signup'),
    path('hr/login/', views.hr_login, name='hr_login'),
    path('candidate/signup/', views.candidate_signup, name='candidate_signup'),
    path('candidate/login/', views.candidate_login, name='candidate_login'),
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('candidate/dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
    path('hr/create-assessment/', views.create_assessment, name='create_assessment'),
    path('hr/view-assessments/', views.view_assessments, name='view_assessments'),
    path('hr/view-candidates/', views.view_candidates, name='view_candidates'),
    path('hr/statistics/', views.statistics, name='statistics'),
    path('hr/view-results/', views.view_results, name='view_results'),
    path('logout/', views.logout_view, name='logout'),
    path('hr/assign-assessment/<int:candidate_id>/', views.assign_assessment, name='assign_assessment'),
    path('candidate/take-assessment/<int:assignment_id>/', views.take_assessment, name='take_assessment'),
    path('hr/edit-assessment/<int:assessment_id>/', views.edit_assessment, name='edit_assessment'),  # New
    path('hr/delete-assessment/<int:assessment_id>/', views.delete_assessment, name='delete_assessment'),  # New
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)