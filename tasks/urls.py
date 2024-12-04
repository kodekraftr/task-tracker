# tasks/urls.py
from django.urls import path
from .views import *
urlpatterns = [
    path('tasks/', TaskCreateView.as_view(), name='task-create'),  # Create a new task
    path('tasks/<int:task_id>/', TaskUpdateView.as_view(), name='task-update'),  # Update a task
    path('tasks/<int:task_id>/delete/', TaskDeleteView.as_view(), name='task-delete'),  # Delete a task
    path('tasks/<int:task_id>/assign/', AssignTaskView.as_view(), name='assign-task'),  # Assign task
    path('tasks/assigned/', ListAssignedTasksView.as_view(), name='list-assigned-tasks'),  # List all assigned tasks
    path('tasks/<int:task_id>/status/', UpdateTaskStatusView.as_view(), name='update-task-status'),  # Update task status
    path('tasks/<int:task_id>/request-change/', RequestTaskChangeView.as_view(), name='request-task-change'),  # Request task change
    path('tasks/<int:task_id>/review/', TaskReviewView.as_view(), name='task-review'),  # Add rating and comments
    path('tasks/<int:task_id>/review/', TaskReviewDetailView.as_view(), name='task-review-detail'),  # View rating and comments
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/read/', MarkAsReadView.as_view(), name='mark-as-read'),
]
