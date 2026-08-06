from datetime import timedelta
import json
from urllib import request

from django.db.models import Count, Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.views.generic import TemplateView

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (CreateView, ListView, DetailView, UpdateView, DeleteView)

from .forms import JobApplicationForm, UserProfileForm, UserSettingsForm, ResumeAIForm

from .services.resume_ai import (ResumeAIError, tailor_resume,)

from .models import JobApplication, UserSettings
from .models import UserSettings

# Create your views here.
def home_page_view(request):
    """
    Display a public welcome page when logged out.

    Display the user's application dashboard when logged in.
    """

    if not request.user.is_authenticated:
        return render(
            request,
            "applications/home.html",
        )

    applications = (
        JobApplication.objects
        .filter(user=request.user)
        .prefetch_related("interactions")
    )

    # ---------------------------------
    # Main application counts
    # ---------------------------------

    total_applications = applications.count()

    active_statuses = [
        "applied",
        "screening",
        "interview",
    ]

    active_applications = applications.filter(
        status__in=active_statuses,
    ).count()

    active_interviews = applications.filter(
        status="interview",
    ).count()

    offers_count = applications.filter(
        status="offer",
    ).count()

    rejected_count = applications.filter(
        status="rejected",
    ).count()

    # ---------------------------------
    # Average response time
    # ---------------------------------
    #
    # Response time is measured from:
    #
    # application.applied_date
    #          ↓
    # first recorded interaction
    #
    # Applications without both dates
    # are ignored.

    response_times = []

    for application in applications:
        if not application.applied_date:
            continue

        first_interaction = (
            application.interactions
            .order_by("date")
            .first()
        )

        if not first_interaction:
            continue

        response_days = (
            first_interaction.date
            - application.applied_date
        ).days

        if response_days >= 0:
            response_times.append(response_days)

    if response_times:
        average_response_time = round(
            sum(response_times) / len(response_times),
            1,
        )
    else:
        average_response_time = None

    # ---------------------------------
    # Recent applications
    # ---------------------------------

    recent_applications = applications.order_by(
        "-created_at"
    )[:5]

    # ---------------------------------
    # Stale applications
    # ---------------------------------
    #
    # An application needs attention when:
    #
    # - It has not been updated for 14 days.
    # - It is still active.
    # - It has not been rejected, withdrawn,
    #   or converted into an offer.

    user_settings, created = UserSettings.objects.get_or_create(
        user=request.user
    )

    stale_cutoff = (
        timezone.now()
        - timedelta(
            days=user_settings.stale_application_days
        )
    )

    stale_applications = applications.filter(
        updated_at__lt=stale_cutoff,
        status__in=active_statuses,
    ).order_by("updated_at")[:10]

    # ---------------------------------
    # Pie chart data
    # ---------------------------------

    status_counts = (
        applications
        .values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )

    status_labels = dict(
        JobApplication.STATUS_CHOICES
    )

    status_chart = {
        "labels": [
            status_labels.get(
                item["status"],
                item["status"].title(),
            )
            for item in status_counts
        ],
        "values": [
            item["total"]
            for item in status_counts
        ],
    }

    context = {
        "total_applications": total_applications,
        "active_applications": active_applications,
        "active_interviews": active_interviews,
        "offers_count": offers_count,
        "rejected_count": rejected_count,
        "average_response_time": average_response_time,
        "recent_applications": recent_applications,
        "stale_applications": stale_applications,
        "status_chart": status_chart,
    }

    return render(
        request,
        "applications/home.html",
        context,
    )

class ApplicationListView(
    LoginRequiredMixin,
    ListView,
):
    model = JobApplication

    template_name = (
        "applications/application_list.html"
    )

    context_object_name = "applications"

    def get_queryset(self):
        queryset = JobApplication.objects.filter(
            user=self.request.user
        )

        query = self.request.GET.get(
            "query",
            "",
        ).strip()

        if query:
            queryset = queryset.filter(
                Q(company__icontains=query)
                | Q(position__icontains=query)
                | Q(location__icontains=query)
                | Q(status__icontains=query)
            )

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_applications = JobApplication.objects.filter(
            user=self.request.user
        )

        context["total_applications"] = (
            all_applications.count()
        )

        context["interview_count"] = (
            all_applications.filter(
                status="interview"
            ).count()
        )

        context["offer_count"] = (
            all_applications.filter(
                status="offer"
            ).count()
        )

        context["rejected_count"] = (
            all_applications.filter(
                status="rejected"
            ).count()
        )

        context["query"] = self.request.GET.get(
            "query",
            "",
        ).strip()

        return context


class ApplicationCreateView(
    LoginRequiredMixin,
    CreateView,
):
    model = JobApplication
    form_class = JobApplicationForm

    template_name = (
        "applications/application_form.html"
    )

    def form_valid(self, form):
        form.instance.user = self.request.user

        return super().form_valid(form)


class ApplicationDetailView(
    LoginRequiredMixin,
    DetailView,
):
    model = JobApplication

    template_name = (
        "applications/application_detail.html"
    )

    context_object_name = "application"

    def get_queryset(self):
        return JobApplication.objects.filter(
            user=self.request.user
        )


class ApplicationUpdateView(
    LoginRequiredMixin,
    UpdateView,
):
    model = JobApplication
    form_class = JobApplicationForm

    template_name = (
        "applications/application_form.html"
    )

    def get_queryset(self):
        return JobApplication.objects.filter(
            user=self.request.user
        )
        
class AnalyticsView(
    LoginRequiredMixin,
    TemplateView
):
    template_name = "applications/analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        applications = JobApplication.objects.filter(
            user=self.request.user
        )

        total_applications = applications.count()

        interview_count = applications.filter(
            status="interview"
        ).count()

        offer_count = applications.filter(
            status="offer"
        ).count()

        rejected_count = applications.filter(
            status="rejected"
        ).count()

        if total_applications > 0:
            interview_rate = round(
                interview_count / total_applications * 100,
                1,
            )

            offer_rate = round(
                offer_count / total_applications * 100,
                1,
            )

            rejection_rate = round(
                rejected_count / total_applications * 100,
                1,
            )
        else:
            interview_rate = 0
            offer_rate = 0
            rejection_rate = 0

        status_counts = (
            applications
            .values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )

        status_labels = dict(
            JobApplication.STATUS_CHOICES
        )

        status_chart = {
            "labels": [
                status_labels.get(
                    item["status"],
                    item["status"].title(),
                )
                for item in status_counts
            ],
            "values": [
                item["total"]
                for item in status_counts
            ],
        }

        monthly_counts = (
            applications
            .annotate(
                month=TruncMonth("created_at")
            )
            .values("month")
            .annotate(total=Count("id"))
            .order_by("month")
        )

        monthly_chart = {
            "labels": [
                item["month"].strftime("%b %Y")
                for item in monthly_counts
                if item["month"]
            ],
            "values": [
                item["total"]
                for item in monthly_counts
                if item["month"]
            ],
        }

        top_companies = (
            applications
            .values("company")
            .annotate(total=Count("id"))
            .order_by("-total", "company")[:5]
        )

        response_times = []

        applications_with_interactions = (
            applications
            .prefetch_related("interactions")
        )

        for application in applications_with_interactions:
            if not application.applied_date:
                continue

            first_interaction = (
                application.interactions
                .order_by("date")
                .first()
            )

            if not first_interaction:
                continue

            response_days = (
                first_interaction.date
                - application.applied_date
            ).days

            if response_days >= 0:
                response_times.append(response_days)

        if response_times:
            average_response_time = round(
                sum(response_times)
                / len(response_times),
                1,
            )
        else:
            average_response_time = None

        context.update(
            {
                "total_applications": total_applications,
                "interview_count": interview_count,
                "offer_count": offer_count,
                "rejected_count": rejected_count,
                "interview_rate": interview_rate,
                "offer_rate": offer_rate,
                "rejection_rate": rejection_rate,
                "average_response_time": average_response_time,
                "status_chart": status_chart,
                "monthly_chart": monthly_chart,
                "top_companies": top_companies,
            }
        )
        return context

# ------------------------------------    
# ---------- Resume AI View ----------
# ------------------------------------

@login_required
def settings_view(request):
    """
    Allow the logged-in user to update profile and
    Application Assistant preferences.
    """

    user_settings, created = UserSettings.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        profile_form = UserProfileForm(
            request.POST,
            instance=request.user,
        )

        settings_form = UserSettingsForm(
            request.POST,
            instance=user_settings,
        )

        if (
            profile_form.is_valid()
            and settings_form.is_valid()
        ):
            profile_form.save()
            settings_form.save()

            messages.success(
                request,
                "Your settings were updated successfully.",
            )

            return redirect(
                "applications:settings"
            )

    else:
        profile_form = UserProfileForm(
            instance=request.user,
        )

        settings_form = UserSettingsForm(
            instance=user_settings,
        )

    context = {
        "profile_form": profile_form,
        "settings_form": settings_form,
    }

    return render(
        request,
        "applications/settings.html",
        context,
    )


@login_required
def resume_ai_view(request):
    analysis = None

    if request.method == "POST":
        form = ResumeAIForm(request.POST)

        if form.is_valid():
            job_requirements = form.cleaned_data[
                "job_requirements"
            ]

            current_resume = form.cleaned_data[
                "current_resume"
            ]

            target_style = form.cleaned_data[
                "target_style"
            ]

            try:
                analysis = tailor_resume(
                    job_requirements=job_requirements,
                    current_resume=current_resume,
                    target_style=target_style,
                )

                messages.success(
                    request,
                    "Your resume analysis was generated successfully.",
                )

            except ResumeAIError as error:
                messages.error(
                    request,
                    str(error),
                )

    else:
        form = ResumeAIForm()

    context = {
        "form": form,
        "analysis": analysis,
    }

    return render(
        request,
        "applications/resume_ai.html",
        context,
    )