from rest_framework.views import APIView
from rest_framework.response import Response
from students.models import Student


class LoginView(APIView):
    def post(self, request):
        vp_code = request.data.get('vp_code')
        
        if not vp_code:
            return Response({"error": "VP code is required"}, status=400)
        try:
            student = Student.objects.get(vp_code=vp_code)
            return Response({
                "id": student.id,
                "name": student.name,
                "email": student.email,  # added email
                "message": "Login successful"
            })
        except Student.DoesNotExist:
            return Response({"error": "Invalid VP code"}, status=400)
        

        
from students.models import Module, Session
from django.utils import timezone
class StartSessionView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        module_id = request.data.get('module_id')
        session = Session.objects.create(
            student_id=student_id,
            module_id=module_id,
            check_in=timezone.now()
        )
        return Response({"session_id": session.id,
                         "message": "Session started" })
    


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Session
class UpdateProgressView(APIView):
    def put(self, request, session_id):
        progress = request.data.get('progress')
        try:
            session = Session.objects.get(id=session_id)
            session.progress = progress
            session.save()
            return Response({"message": "Progress updated"})
        except:
            return Response({"error": "Invalid session ID"}, status=400)



from django.utils import timezone
class EndSessionView(APIView):
    def post(self, request, session_id):
        try:
            session = Session.objects.get(id=session_id)
            session.check_out = timezone.now()
            session.save()
            return Response({"message": "Session ended"})
        except:
            return Response({"error": "Invalid session ID"}, status=400)
        

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Module
class GetModuleList(APIView):
    def get(self, request):
        modules = Module.objects.all()
        data = [{"id": m.id, "name": m.name} for m in modules]
        return Response(data)









# students/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import AdminUser
from django.contrib.auth.hashers import check_password

def admin_login_view(request):
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        password = request.POST.get('password')

        try:
            user = AdminUser.objects.get(staff_id=staff_id)
            if check_password(password, user.password):
                request.session['admin_user_id'] = user.id
                print(f"Admin user {user.name} logged in successfully.")
                return redirect('admin_dashboard')  # Redirect to your dashboard view
            else:
                messages.error(request, "Invalid password.")
        except AdminUser.DoesNotExist:
            messages.error(request, "Staff ID not found.")

    return render(request, 'admin-sign-in.html')


from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models.functions import TruncMonth
from students.models import Student, Module, Session
from .models import AdminUser
from datetime import datetime

def admin_dashboard_view(request):
    admin_id = request.session.get('admin_user_id')
    if not admin_id:
        return redirect('admin_login')

    admin = AdminUser.objects.get(id=admin_id)

    # Totals
    total_students = Student.objects.count()
    total_modules = Module.objects.count()
    total_sessions = Session.objects.count()

    # Students joined per month (dynamic)
    students_by_month = (
        Student.objects.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    labels = [entry['month'].strftime('%b %Y') for entry in students_by_month]
    data = [entry['count'] for entry in students_by_month]

    # Dynamically get latest month and previous month counts
    current_month = datetime.now().replace(day=1)
    current_count = Student.objects.filter(created_at__gte=current_month).count()

    # previous month logic
    if students_by_month and len(students_by_month) >= 2:
        previous_count = students_by_month[-2]['count']
    else:
        previous_count = 0

    if previous_count != 0:
        percent_change = ((current_count - previous_count) / previous_count) * 100
    else:
        percent_change = 0

    # Most active module
    most_active_module = (
        Session.objects.values('module__name')
        .annotate(session_count=Count('id'))
        .order_by('-session_count')
        .first()
    )

    most_active_module_name = most_active_module['module__name'] if most_active_module else 'No data'
    session_count = most_active_module['session_count'] if most_active_module else 0

    return render(request, 'dashboard.html', {
        'admin': admin,
        'total_students': total_students,
        'total_modules': total_modules,
        'total_sessions': total_sessions,
        'percent_change': round(percent_change, 2),
        'most_active_module': most_active_module_name,
        'most_active_count': session_count,
        'labels': labels,
        'data': data,
    })
