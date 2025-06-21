from django import test
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
                return redirect('admin_dashboard')  # ✅ Only on success
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
        # Recent active students (latest 5 check-ins)
    recent_sessions = (
        Session.objects.select_related('student', 'module')
        .order_by('-check_in')[:5]
    )

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

    categories = [
        {
            "icon": "ni-mobile-button",
            "title": "Total Modules",
            "description": f"{total_modules} modules available, ",
            "highlight": f"{total_sessions} sessions conducted",
        },
        {
            "icon": "ni-tag",
            "title": "Student Registrations",
            "description": f"New this month: ",
            "highlight": f"{current_count}",
        },
        {
            "icon": "ni-box-2",
            "title": "Most Active Module",
            "description": f"Sessions in this module: ",
            "highlight": f"{session_count}",
        },
        {
            "icon": "ni-satisfied",
            "title": "Recent Sessions",
            "description": f"Latest check-ins: ",
            "highlight": f"{recent_sessions.count()}",
        },
    ]

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
        'recent_sessions': recent_sessions,
        'categories': categories,  # pass categories to template
    })


from django.shortcuts import render
from .models import Student  # Adjust based on your model name

def student_profile(request):
    students = Student.objects.all()
    return render(request, 'student_profile.html', {'students': students})

def add_student(request):
    if request.method == 'POST':
        # Handle form submission
        pass
    return render(request, 'add_student.html')



# views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Student
from .forms import StudentForm  # you'll create this

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_profile') 
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'edit_student.html', {'form': form, 'student': student})




from django.views.decorators.http import require_POST
from django.contrib import messages

@require_POST
def bulk_delete_students(request):
    selected_ids = request.POST.getlist('selected_ids')
    if selected_ids:
        Student.objects.filter(id__in=selected_ids).delete()
        messages.success(request, f"Deleted {len(selected_ids)} students successfully.")
    else:
        messages.warning(request, "No students selected.")
    return redirect('student_profile')




from django.shortcuts import render, redirect
from .models import Student

def add_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        vp_code = request.POST.get('vp_code')
        
        Student.objects.create(name=name, email=email, vp_code=vp_code)
        return redirect('student_profile')

    return render(request, 'student_add.html')


#  module section started
from .models import Module
from django.shortcuts import render

def module_list_view(request):
    modules = Module.objects.all()
    return render(request, 'module_list.html', {'modules': modules})

# views.py

from django.shortcuts import render, redirect
from .models import Module

def add_module(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        Module.objects.create(name=name)
        return redirect('module_list')  # or any URL name you define for listing modules

    return render(request, 'module_add.html')  # HTML form template


def edit_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        module.name = name
        module.description = description
        module.save()
        return redirect('module_list')  # or any URL name you define for listing modules
    
    return render(request, 'edit_module.html', {'module': module})  # HTML form template

from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import redirect
from .models import Module  # Ensure this is imported

@require_POST
def bulk_delete_modules(request):
    selected_ids = request.POST.getlist('selected_ids')
    print("Selected for deletion:", selected_ids)
    if selected_ids:
        Module.objects.filter(id__in=selected_ids).delete()
        messages.success(request, f"Deleted {len(selected_ids)} modules successfully.")
    else:
        messages.warning(request, "No modules selected.")
    return redirect('module_list')



from django.shortcuts import render, get_object_or_404
from .models import Session

def sessions_list(request):
    sessions = Session.objects.select_related('student', 'module').all()
    return render(request, 'sessions_list.html', {'sessions': sessions})