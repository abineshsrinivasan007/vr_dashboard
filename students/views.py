from django import test
from rest_framework.views import APIView
from rest_framework.response import Response
from students.models import Student
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from students.models import Student
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
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
                "email": student.email,
                "message": "Login successful"
            })
        except Student.DoesNotExist:
            return Response({"error": "Invalid VP code"}, status=400)

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Session
from django.utils import timezone

@method_decorator(csrf_exempt, name='dispatch')
class StartSessionView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        module_id = request.data.get('module_id')
        session = Session.objects.create(
            student_id=student_id,
            module_id=module_id,
            check_in=timezone.now()
        )
        return Response({
            "session_id": session.id,
            "message": "Session started"
        })


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
import requests  # For Google reCAPTCHA

def admin_login_view(request):
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        password = request.POST.get('password')
        recaptcha_response = request.POST.get('g-recaptcha-response')

        # ✅ Step 1: Verify reCAPTCHA with Google
        secret_key = '6LcNu2wrAAAAACQdbuM1dYiOkyAE143FMWXW_KFL'  # Replace with your actual secret key
        recaptcha_data = {
            'secret': secret_key,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=recaptcha_data)
        result = r.json()

        if result.get('success'):
            # ✅ Step 2: Proceed with your login logic
            try:
                user = AdminUser.objects.get(staff_id=staff_id)
                if check_password(password, user.password):
                    request.session['admin_user_id'] = user.id
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, "Invalid password.")
            except AdminUser.DoesNotExist:
                messages.error(request, "Staff ID not found.")
        else:
            # ❌ reCAPTCHA failed
            messages.error(request, "reCAPTCHA verification failed. Please try again.")

    return render(request, 'admin-sign-in.html')


from django.shortcuts import redirect
from django.contrib import messages

def admin_logout(request):
    if 'admin_user_id' not in request.session:
        messages.error(request, "You are not logged in.")
        return redirect('admin_login')
    request.session.flush()  # ✅ Clears session data
    messages.success(request, "You have successfully logged out.")
    return redirect('admin_login')  # Replace with your actual login URL name

from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models.functions import TruncMonth
from students.models import Student, Module, Session
from .models import AdminUser
from datetime import datetime
from django.utils import timezone

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

    # Students joined per month
    students_by_month = list( 
        Student.objects.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    labels = [entry['month'].strftime('%b %Y') for entry in students_by_month]
    data = [entry['count'] for entry in students_by_month]

    # Current month count
    current_month = timezone.now().replace(day=1)
    current_count = Student.objects.filter(created_at__gte=current_month).count()

    # Previous month count safely
    if len(students_by_month) >= 2:
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
            "description": "New this month: ",
            "highlight": f"{current_count}",
        },
        {
            "icon": "ni-box-2",
            "title": "Most Active Module",
            "description": "Sessions in this module: ",
            "highlight": f"{session_count}",
        },
        {
            "icon": "ni-satisfied",
            "title": "Recent Sessions",
            "description": "Latest check-ins: ",
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
        'categories': categories,
    })


def student_profile(request):
    students = Student.objects.all()

    # Attach completed modules count dynamically
    for student in students:
        student.completed_modules_count = student.session_set.filter(
            progress=100,
            check_out__isnull=False
        ).values('module_id').distinct().count()

    return render(request, 'student_profile.html', {'students': students})


# views.py

from django.shortcuts import render, get_object_or_404, redirect
from students.models import Student, Degree, Department, Section
from students.form import StudentForm

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_profile')  # or wherever you want to redirect
    else:
        form = StudentForm(instance=student)

    # Pass these to use in your manual form dropdowns
    degrees = Degree.objects.all()
    departments = Department.objects.all()
    sections = Section.objects.all()
    
    return render(request, 'edit_student.html', {
        'form': form,
        'student': student,
        'degrees': degrees,
        'departments': departments,
        'sections': sections
    })



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



from django.core.mail import send_mail
from django.contrib import messages
from .models import Degree, Department, Section, Student
def add_student(request):
    context = {
        'degrees': Degree.objects.all(),
        'departments': Department.objects.all(),
        'sections': Section.objects.all(), 
    }

    if request.method == 'POST':
        name = request.POST.get('name')
        degree_id = request.POST.get('degree')
        department_id = request.POST.get('department')
        section_id = request.POST.get('section')
        email = request.POST.get('email')
        vp_code = request.POST.get('vp_code')
        context={
            'name': name,
            'degree_id': degree_id,
            'department_id': department_id,
            'section_id': section_id,
            'email': email,
            'vp_code': vp_code,
        }
        print('context',context)
        if not all([degree_id, department_id, section_id]):
            messages.error(request, "Please select all dropdowns (Degree, Department, Section).")
            return render(request, 'student_add.html', context)

        try:
            degree = Degree.objects.get(id=int(degree_id))
            department = Department.objects.get(id=int(department_id))
            section = Section.objects.get(id=int(section_id))
        except (ValueError, Degree.DoesNotExist, Department.DoesNotExist, Section.DoesNotExist) as e:
            messages.error(request, f"Invalid selection: {e}")
            return render(request, 'student_add.html', context)

        # Validate hierarchy
        if department.degree.id != degree.id:
            messages.error(request, "Selected department does not belong to the chosen degree.")
            return render(request, 'student_add.html', context)

        if section.department.id != department.id:
            messages.error(request, "Selected section does not belong to the chosen department.")
            return render(request, 'student_add.html', context)

        student = Student.objects.create(
            name=name,
            email=email,
            vp_code=vp_code,
            degree=degree,
            department=department,
            section=section
        )
        # Send welcome email
        subject = 'Welcome to the Student Portal'
        message = f'''Hi {name},

Welcome to the Student Portal!

Your profile has been created successfully.

🎓 Degree: {degree.name}
🏢 Department: {department.name}
📘 Section: {section.section}
🔑 Your VP Code: {vp_code}

You’ll need this VP Code to log in or access your profile.

Best regards,
Admin Team
'''
        try:
            send_mail(
                subject,
                message,
                'abinesh70103@gmail.com',
                [email],
                fail_silently=False,
            )
        except Exception as e:
            messages.warning(request, f"Student created but email sending failed: {e}")
            return redirect('student_profile')

        messages.success(request, "Student added and email sent successfully.")
        return redirect('student_profile')

    return render(request, 'student_add.html', context)


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
        Module.objects.create(name=name,description=description)
        
        return redirect('module_list')  # or any URL name you define for listing modules

    return render(request, 'module_add.html')  # HTML form template


def edit_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        print("description",description)
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


    # Prepare filter values
    degrees = Degree.objects.values_list('name', flat=True).distinct()
    departments = Department.objects.all()
    if degree_name:
        departments = departments.filter(degree__name=degree_name)
    departments = departments.values_list('name', flat=True).distinct()

    sections = Section.objects.all()
    if department_name:
        sections = sections.filter(department__name=department_name)
    sections = sections.values_list('section', flat=True).distinct()

    return render(request, 'sessions_list.html', {
        'sessions': sessions,
        'degrees': degrees,
        'departments': departments,
        'sections': sections,
        'selected_degree': degree_name,
        'selected_department': department_name,
        'selected_section': section_name,
    })



from django.shortcuts import render
from .models import Session

def sessions_list(request):
    sessions = Session.objects.select_related(
    'student',
    'student__degree',
    'student__department',
    'student__section',
    'module'
).all()


    context = {
        'sessions': sessions,
    }
    return render(request, 'sessions_list.html', context)

from students.models import Department, Degree

def departments_list_view(request):
    departments = Department.objects.all()
    return render(request, 'departments_list.html', {'departments': departments})



from django.http import JsonResponse

def load_departments(request):
    degree_id = request.GET.get('degree_id')
    departments = Department.objects.filter(degree_id=degree_id).values('id', 'name')
    return JsonResponse(list(departments), safe=False)

def load_sections(request):
    department_id = request.GET.get('department_id')
    sections = Section.objects.filter(department_id=department_id).values('id', 'section')
    return JsonResponse(list(sections), safe=False)




# views.py
import openpyxl
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Student

@user_passes_test(lambda u: u.is_staff)
@login_required
def export_student_report(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Student Report"

    # Headers
    ws.append(["Name", "VP Code", "Degree", "Department", "Section", "Email"])

    # Data
    for student in Student.objects.select_related('degree', 'department', 'section'):
        ws.append([
            student.name,
            student.vp_code,
            student.degree.name if student.degree else '',
            student.department.name if student.department else '',
            student.section.section if student.section else '',
            student.email if student.email else '',
        ])

    # Return Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=student_report.xlsx'
    wb.save(response)
    return response


import openpyxl
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Session

@login_required
@user_passes_test(lambda u: u.is_staff)
def export_session_report(request):
 
    if request.method == 'GET':
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Session Report"

        # Header row
        ws.append([
            "Student Name", "VP Code", "Module", "Degree",
            "Department", "Section", "Check-In", "Check-Out", "Progress"
        ])

        # Session data
        sessions = Session.objects.select_related(
            'student', 'module', 'student__degree',
            'student__department', 'student__section'
        )
        print(f"Exporting {sessions.count()} sessions")

        for session in sessions:
            ws.append([
                session.student.name,
                session.student.vp_code,
                session.module.name,
                session.student.degree.name if session.student.degree else '',
                session.student.department.name if session.student.department else '',
                session.student.section.section if session.student.section else '',
                session.check_in.strftime('%Y-%m-%d %H:%M:%S') if session.check_in else '',
                session.check_out.strftime('%Y-%m-%d %H:%M:%S') if session.check_out else '',
                f"{session.progress}%",
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=session_report.xlsx'
        wb.save(response)
        return response

    return HttpResponse("Method not allowed", status=405)



import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import AdminMessage

@csrf_exempt
def send_admin_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message_text = data.get('message')
        if message_text:
            # Save message
            msg = AdminMessage.objects.create(message=message_text)

            # Send message to channel layer group 'students_group'
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'students_group',
                {
                    'type': 'chat_message',  # handler function in consumer
                    'message': message_text,
                    'timestamp': str(msg.timestamp),
                }
            )
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)



def notification_admin(request):
    return render(request, 'notification_admin.html')