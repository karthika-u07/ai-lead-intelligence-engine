from django.urls import path
from .views import LeadCreateAPIView, LeadDetailAPIView, LeadListAPIView

urlpatterns = [
    path("leads/", LeadCreateAPIView.as_view()),
    path("leads/<int:pk>/", LeadDetailAPIView.as_view()),
    path("leads/all/", LeadListAPIView.as_view()),

]


