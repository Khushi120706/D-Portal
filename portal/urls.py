from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('govt_job/', views.govt_job, name='govt_job'),
    path('private_job/', views.private_job, name='private_job'),
    path('explore_job/', views.explore_job, name='explore_job'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('candidate_dashboard/', views.c_dashboard, name='dashboard'),
    path('employee_dashboard/', views.e_dashboard, name='employer'),
    path('profile/', views.profile, name='profile'),
    path('job/<int:id>/', views.job_detail, name='job_detail'),
    path('apply/<int:id>/', views.apply_job, name='apply_job'),
    path('applied_job', views.applied_job, name='applied_job'),
    path('company_profile/', views.company_profile, name='company_profile'),
    path("post_job/", views.post_job, name="post_job"),
    path("view_application/", views.view_application, name="view_application"),
    path('update-application/<int:id>/', views.update_application, name='update_application'),
    path("admin_page/", views.admin, name="admin"),
    path('approve/<int:id>/', views.approve_employer, name='approve_employer'),
    path('reject/<int:id>/', views.reject_employer, name='reject_employer'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('logout/', views.logout_view, name='logout'), 
    path('verify/<int:app_id>/', views.camera_verify, name='camera_verify'),
    path('verification/<int:app_id>/', views.verify_candidate, name='verify_candidate'),
    path('verification/approve/<int:verification_id>/', views.approve_verification, name='approve_verification'),
    path('verification/reject/<int:verification_id>/', views.reject_verification, name='reject_verification'),
    path('delete-job/<int:id>/', views.delete_job, name='delete_job'),
    path('delete_employer/<int:employer_id>/', views.delete_employer, name='delete_employer')
]