from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserData.as_view()),
]