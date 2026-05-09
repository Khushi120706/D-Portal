from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import User, CandidateProfile, Employer
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Application, Job, CandidateProfile
from .models import Employer
from .models import Contact
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import Contact
import base64
from django.core.files.base import ContentFile
from .models import Verification
from django.shortcuts import  get_object_or_404
from .forms import EmployerForm
from django.contrib.auth import login
from .models import *


# Create your views here.
# ======================== home page ===================================


def home(request):
    jobs = Job.objects.all().order_by('-id')[:6]
    return render(request, 'home.html', {'jobs': jobs})

# ========================= about page ==================================
def about(request):
    return render(request, 'about.html')

# ================================ contact page ======================================

def contact(request):

    if request.method == "POST":

        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # ✅ DATABASE me save
        Contact.objects.create(
            name=name,
            email=email,
            message=message
        )

        # ✅ EMAIL send
        full_message = f"""
        New Contact Message:

        Name: {name}
        Email: {email}
        Message: {message}
        """

        send_mail(
            subject="New Contact Message",
            message=full_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
        )

        return render(request, 'contact.html', {'success': 'Message sent successfully'})

    return render(request, 'contact.html')
# =============================== govt job page =========================
def govt_job(request):
    jobs = Job.objects.filter(job_type="Government")

    q = request.GET.get('q')
    location = request.GET.get('location')
    department = request.GET.get('department')

    if q:
        jobs = jobs.filter(title__icontains=q)

    if location:
        jobs = jobs.filter(location=location)

    if department:
        jobs = jobs.filter(department=department)

    return render(request, 'govt_job_page.html', {'jobs': jobs})

#  ============================== private job page ==========================
def private_job(request):
    jobs = Job.objects.filter(job_type="Private")

    q = request.GET.get('q')
    location = request.GET.get('location')
    skills = request.GET.get('skills')

    if q:
        jobs = jobs.filter(title__icontains=q)

    if location:
        jobs = jobs.filter(location=location)

    if skills:
        jobs = jobs.filter(skills__icontains=skills)

    return render(request, 'private_job_page.html', {'jobs': jobs})

# ================================== Exploar job page ================================
def explore_job(request):
    jobs = Job.objects.all()

    q = request.GET.get('q')
    job_type = request.GET.get('type')
    location = request.GET.get('location')

    if q:
        jobs = jobs.filter(title__icontains=q)

    if job_type:
        jobs = jobs.filter(job_type=job_type)

    if location:
        jobs = jobs.filter(location=location)

    return render(request, 'explore_job.html', {'jobs': jobs})
 
# =================================== register page =================================
# def register_view(request):
#     if request.method == "POST":
#         user_type = request.POST.get('user_type')
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         # Create user
#         user = User.objects.create_user(
#             username=email,
#             email=email,
#             password=password,
#             role=user_type
#         )

#         if user_type == "candidate":
#             CandidateProfile.objects.create(
#                 user=user,
#                 phone=request.POST.get('phone'),
#                 disability_type=request.POST.get('disability_type'),
#                 disability_percentage=request.POST.get('disability_percentage'),
#                 skills=request.POST.get('skills'),
#                 education=request.POST.get('education'),
#                 profile=request.FILES.get('profile'),
#                 disability_doc=request.FILES.get('disability_doc'),
#                 resume=request.FILES.get('resume'),
#             )

#         elif user_type == "employer":
#             Employer.objects.create(
#                 user=user,
#                 company_name=request.POST.get('company_name'),
#                 industry=request.POST.get('industry'),
#                 description=request.POST.get('description'),
#             )

#         return redirect('login')

#     return render(request, 'register.html')


def register_view(request):
    if request.method == "POST":
        user_type = request.POST.get('user_type')

        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        if user_type == "candidate":
            user.role = "candidate"
            user.first_name = request.POST.get('name')
            user.save()

            CandidateProfile.objects.create(
                user=user,
                phone=request.POST.get('phone'),
                disability_type=request.POST.get('disability_type'),
                disability_percentage=request.POST.get('disability_percentage'),
                skills=request.POST.get('skills'),
                education=request.POST.get('education'),
                profile=request.FILES.get('profile'),
                disability_doc=request.FILES.get('disability_doc'),
                resume=request.FILES.get('resume')
            )

            login(request, user)
            return redirect('dashboard')

        elif user_type == "employer":
            user.role = "employer"
            user.save()

            Employer.objects.create(
                user=user,
                company_name=request.POST.get('company_name'),
                industry=request.POST.get('industry'),
                description=request.POST.get('description')
            )

            login(request, user)
            return redirect('employer')

    return render(request, 'register.html')
# =================================== login page =====================================

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')

        user = authenticate(request, username=email, password=password)

        if user is not None:

            if user.role.lower() != selected_role.lower():
                return render(request, 'login.html', {'error': 'Role mismatch'})

            login(request, user)

            if user.role == "candidate":
                return redirect('dashboard')

            elif user.role == "employer":
                return redirect('employer')

            elif user.role == "admin":
                return redirect('admin')

        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

# ======================================== candidate dashboard ========================================================================


@login_required
def c_dashboard(request):
    if request.user.role != "candidate":
        return redirect('login')

    user = request.user
    profile = CandidateProfile.objects.get(user=user)

    total_applications = Application.objects.filter(user=user).count()
    shortlisted = Application.objects.filter(user=user, status="Accepted").count()

    # Selected jobs (Accepted)
    selected_jobs = Application.objects.filter(user=user, status="Accepted")

    # Rejected jobs
    rejected_jobs = Application.objects.filter(user=user, status="Rejected")

    # Pending / applied but not decided
    applied_jobs = Application.objects.filter(user=user).exclude(status__in=["Accepted","Rejected"])

    # ✅ Profile Completion
    fields = [
        profile.skills,
        profile.education,
        profile.disability_type,
        profile.profile,
        profile.resume,
        profile.disability_doc,
        profile.phone
    ]
    filled = sum(1 for f in fields if f)
    profile_completion = int((filled / len(fields)) * 100)

    # Relevant jobs for suggestion
    jobs = Job.objects.filter(disability_type=profile.disability_type)[:5]

    return render(request, 'c_dashboard.html', {
        'profile': profile,
        'profile_completion': profile_completion,
        'total_applications': total_applications,
        'shortlisted': shortlisted,
        'jobs': jobs,
        'applied_jobs': applied_jobs,
        'selected_jobs': selected_jobs,
        'rejected_jobs': rejected_jobs
    })

# ==================================== profile page ========================================
@login_required
def profile(request):

    if request.user.role != "candidate":
        return redirect('login')

    user = request.user
    profile = CandidateProfile.objects.get(user=user)

    if request.method == "POST":
        user.first_name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.save()

        profile.phone = request.POST.get('phone')
        profile.disability_type = request.POST.get('disability_type')
        profile.disability_percentage = request.POST.get('disability_percentage')
        profile.skills = request.POST.get('skills')
        profile.education = request.POST.get('education')

        if request.FILES.get('profile'):
            profile.profile = request.FILES.get('profile')

        if request.FILES.get('resume'):
            profile.resume = request.FILES.get('resume')

        if request.FILES.get('disability_doc'):
            profile.disability_doc = request.FILES.get('disability_doc')

        profile.save()

    return render(request, 'profile.html', {'profile': profile})

# ============================================ job details page ==========================================
def job_detail(request, id):
    job = Job.objects.get(id=id)

    profile = None
    disability_ok = False   # 👈 NEW

    if request.user.is_authenticated and request.user.role == "candidate":
        profile = CandidateProfile.objects.get(user=request.user)

        # ✅ SAFE CHECK
        if profile.disability_percentage < 50:
            disability_ok = True

    # ✅ benefits fix
    benefits_list = job.benefits.split(',') if job.benefits else []

    return render(request, 'job_details.html', {
        'job': job,
        'profile': profile,
        'benefits_list': benefits_list,
        'disability_ok': disability_ok   # 👈 SEND THIS
    })
# ======================================= applied job page ========================================
@login_required
def apply_job(request, id):

    if request.user.role != "candidate":
        return redirect('login')

    job = Job.objects.get(id=id)
    if Application.objects.filter(user=request.user, job=job).exists():
        return redirect('applied_job')
    profile = CandidateProfile.objects.get(user=request.user)

# 🔥 CONDITION ADD
    if int(profile.disability_percentage) > 50:
        return render(request, 'job_details.html', {
        'job': job,
        'error': 'Only candidates with less than 50% disability can apply ❌'
    })

# ✅ ALLOW APPLY
    Application.objects.create(
        user=request.user,
        job=job,
        resume=profile.resume,
        disability_percentage=profile.disability_percentage
    )

    return redirect('applied_job')

@login_required
def applied_job(request):

    if request.user.role != "candidate":
        return redirect('login')

    applications = Application.objects.filter(user=request.user)

    return render(request, 'applied_job.html', {'applications': applications})
#  ===================================== employer dashboard ======================================
@login_required
def e_dashboard(request):

    # 🔒 ROLE CHECK
    if request.user.role != "employer":
        return redirect('login')

    user = request.user
    company = Employer.objects.get(user=user)

    jobs = Job.objects.filter(employer=company)

    total_jobs = jobs.count()
    total_applications = Application.objects.filter(job__in=jobs).count()
    shortlisted = Application.objects.filter(job__in=jobs, status="Accepted").count()

    # 🔥 NEW: verification data
    verifications = Verification.objects.filter(status="pending")

    context = {
        'company': company,
        'jobs': jobs,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'shortlisted': shortlisted,
        'verifications': verifications   # 👈 Important for camera verify
    }

    return render(request, 'e_dashboard.html', context)


# ======================================= company progile page =======================================

@login_required
def company_profile(request):

    # check existing employer
    employer = Employer.objects.filter(user=request.user).first()

    if request.method == "POST":
        form = EmployerForm(request.POST, request.FILES, instance=employer)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user   # 🔥 VERY IMPORTANT
            obj.save()

            return redirect('employer')
        else:
            print(form.errors)  # debug

    else:
        form = EmployerForm(instance=employer)

    return render(request, 'company_profile.html', {'form': form})


# ======================================== post job =====================================================
@login_required
def post_job(request):

    if request.user.role != "employer":
        return redirect('login')

    company = Employer.objects.get(user=request.user)

    if request.method == "POST":

        title = request.POST.get('title')
        job_type = request.POST.get('job_type')
        department = request.POST.get('department')
        location = request.POST.get('location')
        last_date = request.POST.get('last_date')
        skills = request.POST.get('skills')
        disability_type = request.POST.get('disability_type')
        disability_percent = request.POST.get('disability_percent')
        salary = request.POST.get('salary')
        description = request.POST.get('description')

        # ✅ NEW (IMPORTANT)
        benefits = request.POST.get('benefits')

        # 🔥 VALIDATION
        if not title:
            return render(request, 'post_job.html', {'error': 'Title is required'})

        Job.objects.create(
            employer=company,
            title=title,
            job_type=job_type,
            department=department,
            location=location,
            skills=skills,
            disability_type=disability_type,
            disability_percent=disability_percent,
            salary=salary,
            description=description,
            benefits=benefits,  # ✅ ADD THIS
            last_date=last_date   # 👈 ADD THIS
        )

        return redirect('employer')

    return render(request, 'post_job.html')

# ============================================ view application ========================================
@login_required
def view_application(request):

    if request.user.role != "employer":
        return redirect('login')

    company = Employer.objects.get(user=request.user)
    jobs = Job.objects.filter(employer=company)

    applications = Application.objects.filter(job__in=jobs)

    return render(request, 'view_application.html', {'applications': applications})

@login_required
def update_application(request, id):

    if request.user.role != "employer":
        return redirect('login')

    app = Application.objects.get(id=id)

    action = request.POST.get('action')

    if action == "accept":
        app.status = "Accepted"
    elif action == "reject":
        app.status = "Rejected"

    app.save()

    return redirect('view_application')


# =================================== admin page ===============================================

User = get_user_model()

@login_required
def admin(request):

    # 🔒 DOUBLE SECURITY
    if not request.user.is_superuser:
        return redirect('login')

    total_users = User.objects.count()
    total_jobs = Job.objects.count()

    pending_employers = Employer.objects.filter(is_approved=False)

    context = {
        'total_users': total_users,
        'total_jobs': total_jobs,
        'pending_employers': pending_employers,
        'pending_employers_count': pending_employers.count(),
        'jobs': Job.objects.all(),
        'users': User.objects.all(),
        'employers': Employer.objects.all(),
    }

    return render(request, 'admin_page.html', context)
# ✅ APPROVE
@login_required
def approve_employer(request, id):
    if request.method == "POST":
        employer = get_object_or_404(Employer, id=id)
        employer.is_approved = True   # 🔥 MAIN FIX
        employer.save()
    return redirect('admin')


# ✅ REJECT
@login_required
def reject_employer(request, id):
    if request.method == "POST":
        employer = get_object_or_404(Employer, id=id)
        employer.is_approved = False
        employer.save()
    return redirect('admin')



@login_required
def delete_user(request, user_id):

    # 🔒 only admin
    if not request.user.is_superuser:
        return redirect('login')

    user = get_object_or_404(User, id=user_id)

    # ❗ admin khud ko delete na kare
    if user == request.user:
        return redirect('admin')

    # ❗ sirf candidate delete ho (optional safety)
    if user.role != "candidate":
        return redirect('admin')

    user.delete()

    return redirect('admin')

@login_required
def delete_employer(request, employer_id):
    # Only superuser can delete
    if not request.user.is_superuser:
        return redirect('login')

    employer = get_object_or_404(Employer, id=employer_id)
    
    # Delete associated user as well
    employer.user.delete()  # ye employer object ke user ko bhi delete karega
    # Employer object automatically delete ho jayega due to on_delete=CASCADE

    return redirect('admin')  # ya tumhare admin dashboard ka url
 
# ====================================== logout ===================================================
def logout_view(request):
    logout(request)
    return redirect('home')

def camera_verify(request, app_id):
    application = Application.objects.get(id=app_id)

    if request.method == "POST":
        image_data = request.POST.get('image')

        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]

        file = ContentFile(base64.b64decode(imgstr), name='verify.' + ext)

        application.verification_image = file
        application.is_verified = True
        application.status = "Verified"
        application.save()

        return redirect('applied_job')
    
    

def verify_candidate(request, app_id):
    application = get_object_or_404(Application, id=app_id)

    return render(request, 'camera_verify.html', {'application': application})    

@login_required
def approve_verification(request, verification_id):
    v = get_object_or_404(Verification, id=verification_id)
    v.status = 'accepted'
    v.save()
    return redirect('employer')


@login_required
def reject_verification(request, verification_id):
    v = get_object_or_404(Verification, id=verification_id)
    v.status = 'rejected'
    v.save()
    return redirect('employer')


def delete_job(request, id):
    if request.method == "POST":
        job = get_object_or_404(Job, id=id)
        job.delete()
    return redirect('admin')