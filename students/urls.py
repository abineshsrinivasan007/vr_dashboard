from django.urls import path
from students.views import LoginView  
from .views import StartSessionView, UpdateProgressView, EndSessionView
from .views import GetModuleList, admin_login_view, admin_dashboard_view, student_profile, add_student, edit_student, bulk_delete_students,add_student, module_list_view,add_module,edit_module, bulk_delete_modules

urlpatterns = [
    path('login/', LoginView.as_view(), name='student_login'),
    path('start-session/', StartSessionView.as_view()),
    path('update-progress/<int:session_id>/', UpdateProgressView.as_view(), name='update-progress'),
    path('end-session/<int:session_id>/', EndSessionView.as_view(), name='end-session'),
    path('modules/', GetModuleList.as_view(), name='module-list'),
    # Admin URLs
    path('',admin_login_view, name='admin_login'),
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
    # Student URLs
    path('students/', student_profile, name='student_profile'),
    path('students/add/', add_student, name='add_student'), 
    path('students/<int:student_id>/edit/',edit_student, name='edit_student'),
    path('students/delete-selected/', bulk_delete_students, name='bulk_delete_students'),
    path('add-student/', add_student, name='add_student'),
    # Module URLs
    path('modules-list/', module_list_view, name='module_list'),
    path('modules/add/', add_module, name='add_module'),
    
    path('modules/<int:module_id>/edit/', edit_module, name='edit_module'),
    
    path('modules/delete-selected/', bulk_delete_modules, name='bulk_delete_modules'),
]
