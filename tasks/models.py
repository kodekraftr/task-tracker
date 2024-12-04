from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.contrib.auth import get_user_model

User = get_user_model()

# Task Model
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def clean(self):
        if self.end_date <= now():
            raise ValidationError("End date must be in the future.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# Task Assignment Model
class TaskAssignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="assignments")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_tasks")
    status = models.CharField(
        max_length=20,
        choices=[
            ('not started', 'Not Started'),
            ('in progress', 'In Progress'),
            ('completed', 'Completed'),
        ],
        default='not started'
    )
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.task.title} - {self.assigned_to.username}"

class TaskReview(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveSmallIntegerField()
    comments = models.TextField()
    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.task.title}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} - Read: {self.is_read}"

