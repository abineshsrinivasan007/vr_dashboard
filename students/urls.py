from django.urls import path
from students.views import LoginView  
from .views import StartSessionView, UpdateProgressView, EndSessionView
from .views import GetModuleList, admin_login_view, admin_dashboard_view

urlpatterns = [
    path('login/', LoginView.as_view(), name='student_login'),
    path('start-session/', StartSessionView.as_view()),
    path('update-progress/<int:session_id>/', UpdateProgressView.as_view(), name='update-progress'),
    path('end-session/<int:session_id>/', EndSessionView.as_view(), name='end-session'),
    path('modules/', GetModuleList.as_view(), name='module-list'),
    
    path('', admin_login_view, name='admin_login'),
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
]
