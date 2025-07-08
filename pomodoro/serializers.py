from rest_framework import serializers
from .models import User, Project, Tag, Task, Session
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']
        read_only_fields = ['total_focus_time', 'average_focus_time', 'total_sessions']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        otp = user.generate_otp()
        print(f"OTP sent to {user.email}: {otp}")
        return user
    
class CompleteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'gender', 'date_of_birth', 'country']
        read_only_fields = ['email']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data['email']
        otp = data['otp']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        if user.otp_code != otp:
            raise serializers.ValidationError("Invalid OTP.")

        if (timezone.now() - user.otp_created_at).seconds > 300:
            raise serializers.ValidationError("OTP has expired. Please request a new one.")

        user.is_active = True
        user.otp_code = None
        user.otp_created_at = None
        user.save()
        return data


class ForgotPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            otp = user.generate_otp()
            print(f"[Forgot Password] OTP for {user.email}: {otp}")  # Replace with actual email logic
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("No user is associated with this email.")
        
class ForgotPasswordVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data['email']
        otp = data['otp']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        if user.otp_code != otp:
            raise serializers.ValidationError("Invalid OTP.")

        if (timezone.now() - user.otp_created_at).seconds > 300:
            raise serializers.ValidationError("OTP has expired.")

        user.set_password(data['new_password'])
        user.otp_code = None
        user.otp_created_at = None
        user.save()

        return data



class ProjectSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Project
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Tag
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Task
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Session
        fields = '__all__'