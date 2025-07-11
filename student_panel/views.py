# students/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from students.models import Student

def student_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        vp_code = request.POST.get("vp_code")

        try:
            student = Student.objects.get(email=email, vp_code=vp_code)
            
            # Save student session
            request.session['student_id'] = student.id
            request.session['student_name'] = student.name
            request.session.set_expiry(0 if not request.POST.get('remember') else 86400 * 30)  # Session lasts 30 days if "remember me"
            messages.success(request, "Login successful!")
            return redirect('student_dashboard')
        except Student.DoesNotExist:
            messages.error(request, "Invalid email or VP code")
            return redirect('student_login')
    return render(request, 'student_panel/student_login.html')


from students.models import Session, Module
from django.utils.timezone import now
from datetime import datetime

def student_dashboard(request):
    if 'student_id' not in request.session:
        return redirect('student_login')

    student = Student.objects.get(id=request.session['student_id'])

    # Greeting
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    total_modules = Module.objects.count()
    completed_modules = Session.objects.filter(student=student, progress=100).values('module').distinct().count()
    remaining_modules = total_modules - completed_modules

    # Time spent calculation
    sessions = Session.objects.filter(student=student)
    total_seconds = sum([(s.check_out - s.check_in).total_seconds() for s in sessions if s.check_out], 0)
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    # Most used module
    from django.db.models import Count
    most_used = (
        Session.objects.filter(student=student)
        .values('module__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )
    total_minutes = minutes % 60
    total_hours = hours // 60

    most_used_module = most_used['module__name'] if most_used else "N/A"
    completion_percent = int((completed_modules / total_modules) * 100) if total_modules else 0
    remaining_percent = 100 - completion_percent
    return render(request, 'student_panel/dashboard.html', {
        'student': student,
        'greeting': greeting,
        'total_modules': total_modules,
        'completed_modules': completed_modules,
        'remaining_modules': remaining_modules,
        'total_hours': hours,            # <-- Add this
        'total_minutes': minutes, 
        'hours': total_hours,
        'minutes':total_minutes,
        'most_used_module': most_used_module,
        'completion_percent': int((completed_modules / total_modules) * 100) if total_modules else 0,
        'completion_percent': completion_percent,
        'remaining_percent': remaining_percent,
    })