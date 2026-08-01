from django.urls import path

from .views import home_page_view
from . import views 

app_name = 'applications'

urlpatterns = [
    path('', home_page_view, name='home'),
    path('home/', views.home_page_view, name='home')
]