# tasks/serializers.py
from rest_framework import serializers
from .models import Task, TaskAssignment,TaskReview, Notification

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_by', 'created_at', 'end_date']

class TaskAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssignment
        fields = ['id', 'task', 'assigned_to', 'status', 'details']

class TaskReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskReview
        fields = ['id', 'task', 'rating', 'comments', 'reviewed_by', 'reviewed_at']
        read_only_fields = ['reviewed_by', 'reviewed_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'is_read']
        read_only_fields = ['user', 'created_at']

class MarkAsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['is_read']        
