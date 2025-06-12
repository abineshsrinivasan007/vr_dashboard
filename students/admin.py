from django.contrib import admin
from .models import Student, Module, Session

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'vp_code')
    search_fields = ('name', 'vp_code')
    list_display_links = ('id', 'name')  # Make id and name clickable for editing
    list_per_page = 20  # pagination for better readability

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
