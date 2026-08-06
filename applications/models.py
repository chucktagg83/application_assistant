from django.db import models
from django.conf import settings
from django.urls import reverse


# Create your models here.
class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('saved', 'Saved'),
        ('applied', 'Applied'),
        ('screening', 'Screening'),
        ('interviewing', 'Interviewing'),
        ('offer', 'Offer'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_applications",
    )

    company = models.CharField(
        max_length=150,
    )

    position = models.CharField(
        max_length=150,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="saved",
    )

    location = models.CharField(
        max_length=150,
        blank=True,
    )

    job_url = models.URLField(
        max_length=500,
        blank=True,
    )

    contact_name = models.CharField(
        max_length=150,
        blank=True,
    )

    contact_email = models.EmailField(
        blank=True,
    )

    salary = models.CharField(
        max_length=100,
        blank=True,
    )

    applied_date = models.DateField(
        null=True,
        blank=True,
    )

    follow_up_date = models.DateField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.position} at {self.company}"

    def get_absolute_url(self):
        return reverse(
            "applications:application-detail",
            kwargs={"pk": self.pk},
        )
        
class Interaction(models.Model):
    INTERACTION_TYPES = [
        ("phone", "Phone Screen"),
        ("hr", "HR Interview"),
        ("tech", "Technical Interview"),
        ("final", "Final Interview"),
        ("other", "Other"),
    ]

    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="interactions",
    )

    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_TYPES,
    )

    date = models.DateField()

    feedback = models.TextField(
        blank=True,
    )

    outcome = models.CharField(
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.get_interaction_type_display()} - "
            f"{self.application.company}"
        )
        
class UserSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="application_settings",
    )

    email_reminders = models.BooleanField(
        default=True,
    )

    stale_application_days = models.PositiveIntegerField(
        default=14,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Settings for {self.user.username}"