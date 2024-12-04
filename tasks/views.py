from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework import status, permissions,generics
from rest_framework.permissions import IsAuthenticated
from .models import Task, TaskAssignment, TaskReview
from .models import Notification  # Add Notification model
from .serializers import *
from django.core.exceptions import ObjectDoesNotExist

# Task Creation View (No Change for Notifications)
class TaskCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # if request.user.role != 'admin':
        #     return Response({"error": "Only admins can create tasks."}, status=status.HTTP_403_FORBIDDEN)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Task Update View with Notifications
class TaskUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id, created_by=request.user)
        except Task.DoesNotExist:
            return Response({"error": "Task not found or you are not the creator."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Create a notification for the user who is assigned the task
            # for assignment in task.all():  # Assuming you have related name "assignments" in Task model
            #     Notification.objects.create(
            #         user=assignment.assigned_to,  # User assigned to the task
            #         message=f"Task '{task.title}' has been updated.",
            #         is_read=False
            #     )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Task Deletion View with Notifications
class TaskDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id, created_by=request.user)
        except Task.DoesNotExist:
            return Response({"error": "Task not found or you are not the creator."}, status=status.HTTP_404_NOT_FOUND)

        task.delete()

        # Send notification to all users assigned to the task
        for assignment in task.assignments.all():
            Notification.objects.create(
                user=assignment.assigned_to,
                message=f"Task '{task.title}' has been deleted.",
                is_read=False
            )

        return Response({"message": "Task deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# Assign Task View with Notifications
class AssignTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, task_id):
        if request.user.role != 'admin':
            return Response({"error": "Only admins can assign tasks."}, status=status.HTTP_403_FORBIDDEN)

        try:
            task = Task.objects.get(id=task_id, created_by=request.user)
        except Task.DoesNotExist:
            return Response({"error": "Task not found or you are not the creator."}, status=status.HTTP_404_NOT_FOUND)

        user_ids = request.data.get('user_ids', [])
        if not user_ids:
            return Response({"error": "User IDs are required."}, status=status.HTTP_400_BAD_REQUEST)

        assignments = []
        for user_id in user_ids:
            assignment = TaskAssignment(task=task, assigned_to_id=user_id)
            assignment.save()
            assignments.append(assignment)

            # Create a notification for each assigned user
            Notification.objects.create(
                user_id=user_id,
                message=f"Task '{task.title}' has been assigned to you.",
                is_read=False
            )

        serializer = TaskAssignmentSerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Update Task Status View with Notifications
class UpdateTaskStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, task_id):
        try:
            assignment = TaskAssignment.objects.get(task_id=task_id, assigned_to=request.user)
        except TaskAssignment.DoesNotExist:
            return Response({"error": "Task not found or not assigned to you."}, status=status.HTTP_404_NOT_FOUND)

        status = request.data.get('status')
        details = request.data.get('details')

        if status not in ['not started', 'in progress', 'completed']:
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        assignment.status = status
        if details:
            assignment.details = details
        assignment.save()

        # Send a notification about the status change
        Notification.objects.create(
            user=assignment.assigned_to,
            message=f"Task '{assignment.task.title}' status updated to {status}.",
            is_read=False
        )

        serializer = TaskAssignmentSerializer(assignment)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Request Task Change View (No Notification for Now)
class RequestTaskChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, task_id):
        try:
            assignment = TaskAssignment.objects.get(task_id=task_id, assigned_to=request.user)
        except TaskAssignment.DoesNotExist:
            return Response({"error": "Task not found or not assigned to you."}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get('reason')
        if not reason:
            return Response({"error": "Reason for change request is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Logic to handle the request (e.g., notify admin or save request in database)
        return Response({"message": "Change request submitted successfully."}, status=status.HTTP_201_CREATED)


# Task Review Detail View (No Notifications for Now)
class TaskReviewDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            review = TaskReview.objects.get(task=task)
        except TaskReview.DoesNotExist:
            return Response({"error": "No review found for this task."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Task Review View with Notifications
class TaskReviewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, task_id):
        if request.user.role != 'admin':
            raise PermissionDenied("Only admins can add reviews.")

        try:
            task = Task.objects.get(id=task_id, created_by=request.user)
        except Task.DoesNotExist:
            return Response({"error": "Task not found or not created by you."}, status=status.HTTP_404_NOT_FOUND)

        if TaskReview.objects.filter(task=task).exists():
            return Response({"error": "This task already has a review."}, status=status.HTTP_400_BAD_REQUEST)

        rating = request.data.get('rating')
        comments = request.data.get('comments')

        if not (1 <= int(rating) <= 5):
            raise ValidationError("Rating must be between 1 and 5.")

        if not comments:
            raise ValidationError("Comments are required.")

        review = TaskReview.objects.create(
            task=task,
            rating=rating,
            comments=comments,
            reviewed_by=request.user
        )

        # Send a notification to the assigned user about the review
        Notification.objects.create(
            user=task.assigned_to,
            message=f"Your task '{task.title}' has been reviewed. Rating: {rating}, Comment: {comments}",
            is_read=False
        )

        serializer = TaskReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ListAssignedTasksView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        assignments = TaskAssignment.objects.filter(assigned_to=request.user)
        serializer = TaskAssignmentSerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)        

class NotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        # Only fetch notifications for the logged-in user
        return Notification.objects.filter(user=self.request.user)

class MarkAsReadView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MarkAsReadSerializer
    queryset = Notification.objects.all()

    def get_object(self):
        # Fetch the notification by its ID
        obj = Notification.objects.get(id=self.kwargs['notification_id'], user=self.request.user)
        return obj