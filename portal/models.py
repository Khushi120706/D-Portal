from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('candidate', 'Candidate'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    
    
class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    disability_type = models.CharField(max_length=50)
    disability_percentage = models.IntegerField()
    skills = models.TextField()
    education = models.CharField(max_length=100)

    profile = models.ImageField(upload_to='profiles/')
    disability_doc = models.FileField(upload_to='documents/')
    resume = models.FileField(upload_to='resumes/')

    def __str__(self):
        return self.user.username
    

class Employer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    

    company_name = models.CharField(max_length=200)
    hr_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    industry = models.CharField(max_length=100, null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField()
    description = models.TextField()
    logo = models.ImageField(upload_to='company_logo/', null=True, blank=True)

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name   

    
    
    
    
class Job(models.Model):
    JOB_TYPE = (
        ('Government', 'Government'),
        ('Private', 'Private'),
    )

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE)
    department = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    skills = models.TextField()

    disability_type = models.CharField(max_length=100)
    disability_percent = models.IntegerField()
    benefits = models.TextField(null=True, blank=True)

    description = models.TextField()
    salary = models.CharField(max_length=50)
    last_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, default='Active')

    def __str__(self):
        return self.title    
    


class Application(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    resume = models.FileField(upload_to='applications/')
    disability_percentage = models.IntegerField()

    # 🔥 Verification fields
    is_verified = models.BooleanField(default=False)
    verification_image = models.ImageField(upload_to='verification/', null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
        # New field
    is_selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"
    
    
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name    
    
    
class Verification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='verification/')
    status = models.CharField(max_length=20, default='pending')  # pending/approved/rejected    