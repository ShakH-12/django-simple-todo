from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.CreateListTaskView.as_view()),
    path("<int:pk>/", views.TaskDetailView.as_view()),
]
