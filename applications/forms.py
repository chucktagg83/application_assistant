from django import forms
from django.forms import ChoiceField
from django.contrib.auth import get_user_model
from .models import JobApplication

from .models import UserSettings

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication

        fields = [
            "company",
            "position",
            "status",
            "location",
            "job_url",
            "contact_name",
            "contact_email",
            "salary",
            "applied_date",
            "follow_up_date",
            "notes",
        ]

        widgets = {
            "company": forms.TextInput(
                attrs={
                    "placeholder": "Company name",
                }
            ),
            "position": forms.TextInput(
                attrs={
                    "placeholder": "Job title",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "placeholder": "Remote, Denver, Manila, etc.",
                }
            ),
            "job_url": forms.URLInput(
                attrs={
                    "placeholder": "https://...",
                }
            ),
            "contact_name": forms.TextInput(
                attrs={
                    "placeholder": "Recruiter or hiring manager",
                }
            ),
            "contact_email": forms.EmailInput(
                attrs={
                    "placeholder": "name@company.com",
                }
            ),
            "salary": forms.TextInput(
                attrs={
                    "placeholder": "$80,000–$95,000",
                }
            ),
            "applied_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "follow_up_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": "Add interview notes, requirements, or follow-up details...",
                }
            ),
        }
        
        
User = get_user_model()


class UserProfileForm(forms.ModelForm):
    
    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "placeholder": "Username",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "First name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Last name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "name@example.com",
                }
            ),
        }


class UserSettingsForm(forms.ModelForm):
    
    class Meta:
        model = UserSettings

        fields = [
            "email_reminders",
            "stale_application_days",
        ]

        labels = {
            "email_reminders": "Enable email reminders",
            "stale_application_days":
                "Days before an application needs attention",
        }

        widgets = {
            "stale_application_days": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 90,
                }
            ),
        }
        
class ResumeAIForm(forms.Form):
    job_requirements = forms.CharField(
        label="Job Requirements and Expectations",
        min_length=10,
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                "rows": 18,
                "placeholder": (
                    "Paste the job description or requirements here, and ResumeAI will generate a tailored resume for you."
                )
            }
        )
        
    )
    
    current_resume = forms.CharField(
        label="Current Resume",
        min_length=10,
        max_length=30000,
        widget=forms.Textarea(
            attrs={
                "rows": 18,
                "placeholder": ("Paste your current resume here..."
                )
            }
        )
    )
    
    target_style = ChoiceField(
        label="Resume Style",
        choices=[
            ("professional", "Professional"),
            ("technical", "Technical"),
            ("executive", "Executive"),
            ("concise", "Concise"),
        ],
        initial="professional",
    )