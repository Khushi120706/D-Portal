from django import forms
from .models import Employer

class EmployerForm(forms.ModelForm):
    class Meta:
        model = Employer
        fields = [
            'company_name',
            'hr_name',
            'email',
            'phone',
            'website',
            'address',
            'description',
            'logo'
        ]