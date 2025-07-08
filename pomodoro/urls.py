from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    TagViewSet,
    TaskViewSet,
    SessionViewSet,
    RegisterView,
    UserProfileView,
    VerifyOTPView,
    CompleteProfileView,
    ForgotPasswordRequestView,
    ForgotPasswordVerifyView
)

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename='projects')
router.register('tags', TagViewSet, basename='tags')
router.register('tasks', TaskViewSet, basename='tasks')
router.register('sessions', SessionViewSet, basename='sessions')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', UserProfileView.as_view(), name='profile'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('complete-profile/', CompleteProfileView.as_view(), name='complete-profile'),
    path('forgot-password/', ForgotPasswordRequestView.as_view(), name='forgot-password'),
    path('reset-password/', ForgotPasswordVerifyView.as_view(), name='reset-password'),
    path('', include(router.urls)),
]
