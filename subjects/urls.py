# subjects/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("", views.subjects, name="subjects"),
    path("<int:subject_id>/", views.subject_detail, name="subject_detail"),
]
