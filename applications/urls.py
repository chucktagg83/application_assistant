from django.urls import path

from .views import home_page_view
from . import views 

app_name = 'applications'

urlpatterns = [
    path('', home_page_view, name='home'),
    
    path('home/', views.home_page_view, name='home'),
    
    path("analytics/", views.AnalyticsView.as_view(), name="analytics",
),

    path(
        "applications/",
        views.ApplicationListView.as_view(),
        name="application-list",
    ),

    path(
        "applications/create/",
        views.ApplicationCreateView.as_view(),
        name="application-create",
    ),

    path(
        "applications/<int:pk>/",
        views.ApplicationDetailView.as_view(),
        name="application-detail",
    ),

    path(
        "applications/<int:pk>/edit/",
        views.ApplicationUpdateView.as_view(),
        name="application-update",
    ),
    
    path("settings/",
         views.settings_view, 
         name="settings"
    ),
    
    path ("resume-ai/", 
          views.resume_ai_view, 
          name="resume-ai",
    ),
]