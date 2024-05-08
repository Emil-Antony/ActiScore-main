from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.forms.models import inlineformset_factory
from .models import CustomUser, Teacher, Student,StudentRequest, Activity, Category, Subcategory ,Level, Notif, Achievement

CustomUser = get_user_model()

class TeacherInline(admin.TabularInline):
    model = Teacher
    can_delete = False

class StudentInline(admin.TabularInline):
    model = Student
    can_delete = False

class CustomUserAdmin(BaseUserAdmin):
    inlines = (TeacherInline,StudentInline)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'roles','verified', 'is_staff', 'is_superuser')}
        ),
    )
    fieldsets = (
        (None, {'fields': ('username', 'password','roles','verified')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Notif)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Activity)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Level   )
admin.site.register(StudentRequest)
admin.site.register(Achievement)