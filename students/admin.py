from django.contrib import admin
from .models import Student, Module, Session, AdminUser, Degree, Department, Section, AdminMessage

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'staff_id','email','password')
    search_fields=('name','staff_id')
    
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'vp_code','email')
    search_fields = ('name', 'vp_code','email')
    list_display_links = ('id', 'name')  # Make id and name clickable for editing
    list_per_page = 20  # pagination for better readability
@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_display_links = ('id', 'name')
    list_per_page = 20

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'degree', 'name')
    search_fields = ('degree__name', 'name')
    list_display_links = ('id', 'degree', 'name')
    list_per_page = 20

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'section')
    search_fields = ('section',)
    list_display_links = ('id', 'section')
    list_per_page = 20
    
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_display_links = ('id', 'name')
    list_per_page = 20

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'module', 'check_in', 'check_out', 'progress')
    list_filter = ('module',)
    search_fields = ('student__name', 'module__name')
    list_per_page = 20


@admin.register(AdminMessage)
class AdminMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'timestamp')
    