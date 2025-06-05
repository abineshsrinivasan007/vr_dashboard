from django.urls import path
from students.views import LoginView  
from .views import LoginView, StartSessionView, UpdateProgressView, EndSessionView
urlpatterns = [
    path('login/', LoginView.as_view(), name='student_login'),
    path('start-session/', StartSessionView.as_view()),
    path('update-progress/<int:session_id>/', UpdateProgressView.as_view()),
    path('end-session/<int:session_id>/', EndSessionView.as_view()),
]
