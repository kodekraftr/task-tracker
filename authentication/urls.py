from django.urls import path
from .views import RegisterView, LoginView, RoleView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('role/', RoleView.as_view(), name='role'),
]
