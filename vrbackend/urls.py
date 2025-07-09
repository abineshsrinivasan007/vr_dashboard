# vrbackend/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('students.urls')),
    path('student/', include('student_panel.urls')),
]
