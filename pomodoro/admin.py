from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db import transaction
from .models import User, Project, Tag, Task, Session


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'phone_number', 'gender', 'date_of_birth', 'country', 
                 'total_focus_time', 'average_focus_time', 'total_sessions', 
                 'is_active', 'is_staff', 'is_superuser')


@admin.action(description='Force delete selected users')
def force_delete_users(modeladmin, request, queryset):
    with transaction.atomic():
        for user in queryset:
            # Delete related objects first to avoid foreign key constraint issues
            user.session_set.all().delete()
            user.task_set.all().delete()
            user.project_set.all().delete()
            user.tag_set.all().delete()
            user.delete()


class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    actions = [force_delete_users]
    
    list_display = ('email', 'is_staff', 'is_active', 'date_joined', 'total_sessions')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('phone_number', 'gender', 'date_of_birth', 'country')}),
        ('Statistics', {'fields': ('total_focus_time', 'average_focus_time', 'total_sessions')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')


# Register the User model with the custom admin
admin.site.register(User, CustomUserAdmin)

# Register other models
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color')
    list_filter = ('user',)
    search_fields = ('name', 'user__email')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color')
    list_filter = ('user',)
    search_fields = ('name', 'user__email')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'project', 'status', 'estimated_pomodoros')
    list_filter = ('status', 'user', 'project')
    search_fields = ('name', 'user__email')
    filter_horizontal = ('tags',)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'start_time', 'end_time', 'duration')
    list_filter = ('start_time', 'user', 'task')
    search_fields = ('user__email', 'task__name')
    readonly_fields = ('start_time',)