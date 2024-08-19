from django.urls import path
from . import views
from .views import logout_user, register_user, login_user, ProjectListCreateView, ProjectDetailView, MarkNotificationAsReadView, ListNotificationsView
from .views import TaskDetailView, TaskAssignView, TaskListCreateView, DocumentDetailView, DocumentListCreateView, ListTimelineEventsView
urlpatterns = [
    path('', views.UserData.as_view()),
    path('api/register/', register_user, name='register_user'),
    path('api/login/', login_user, name='login'),
    path('api/logout/', logout_user, name='logout_user'),
    path('api/projects/', ProjectListCreateView.as_view(), name='project_list_create'),
    path('api/projects/<int:project_id>/', ProjectDetailView.as_view(), name='project_detail'),
    path('api/tasks/', TaskListCreateView.as_view(), name='task_list_create'),
    path('api/tasks/<int:task_id>/', TaskDetailView.as_view(), name='task_detail'),
    path('api/tasks/<int:task_id>/assign/', TaskAssignView.as_view(), name='task_assign'),
     path('api/documents/', DocumentListCreateView.as_view(), name='document_list_create'),
    path('api/documents/<int:document_id>/', DocumentDetailView.as_view(), name='document_detail'),
    path('api/timeline/', ListTimelineEventsView.as_view(), name='list_timeline_events'),
    path('api/notifications/', ListNotificationsView.as_view(), name='list_notifications'),
    path('api/notifications/<int:id>/mark_read/', MarkNotificationAsReadView.as_view(), name='mark_notification_as_read'),
]