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

from django.shortcuts import render, redirect
from django.contrib import messages
from students.models import Student, Session, Module, AdminMessage
from django.utils.timezone import now
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Count, Avg
import json

def student_dashboard(request):
    if 'student_id' not in request.session:
        return redirect('student_login')

    try:
        student = Student.objects.get(id=request.session['student_id'])
    except Student.DoesNotExist:
        messages.error(request, "Student not found!")
        return redirect('student_login')

    # Greeting
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # Module stats
    total_modules = Module.objects.count()
    completed_modules = Session.objects.filter(student=student, progress=100).values('module').distinct().count()
    remaining_modules = total_modules - completed_modules

    # Time spent safely
    sessions = Session.objects.filter(student=student)
    total_seconds = sum(
        [(s.check_out - s.check_in).total_seconds() for s in sessions if s.check_in and s.check_out],
        0
    )
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    # Most used module safely
    most_used = (
        sessions
        .filter(module__isnull=False)
        .values('module__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )
    most_used_module = most_used['module__name'] if most_used and most_used['module__name'] else "N/A"

    # Completion percentages
    completion_percent = int((completed_modules / total_modules) * 100) if total_modules else 0
    remaining_percent = 100 - completion_percent

    # Monthly completion graph
    labels = []
    monthly_progress = []
    monthly_usage_percentage = []
    today = now()

    for i in range(7, -1, -1):  # Last 8 months
        month_date = today - relativedelta(months=i)
        year = month_date.year
        month = month_date.month

        completed = Session.objects.filter(
            student=student,
            progress=100,
            check_out__year=year,
            check_out__month=month
        ).values('module').distinct().count()

        accessed = Session.objects.filter(
            student=student,
            check_out__year=year,
            check_out__month=month
        ).values('module').distinct().count()

        labels.append(month_date.strftime('%b %Y'))
        monthly_progress.append(completed)
        percentage = int((completed / accessed) * 100) if accessed else 0
        monthly_usage_percentage.append(percentage)

    # Dynamic percentage change
    if len(monthly_progress) >= 2:
        current = monthly_progress[-1]
        previous = monthly_progress[-2]
        change_percent = round(((current - previous) / previous) * 100) if previous else (100 if current > 0 else 0)
    else:
        change_percent = 0

    trend_direction = "up" if change_percent >= 0 else "down"
    trend_class = "text-success" if change_percent >= 0 else "text-danger"
    trend_icon = "fa-arrow-up" if change_percent >= 0 else "fa-arrow-down"

    # Module summary safely
    module_summary = []
    student_modules = sessions.filter(module__isnull=False).values('module').distinct()
    for entry in student_modules:
        module_id = entry['module']
        try:
            module = Module.objects.get(id=module_id)
        except Module.DoesNotExist:
            continue

        module_sessions = sessions.filter(module=module)
        total_time = sum(
            [(s.check_out - s.check_in).total_seconds() for s in module_sessions if s.check_in and s.check_out],
            0
        )
        time_spent_minutes = int(total_time // 60)
        progress_list = module_sessions.values_list('progress', flat=True)
        avg_progress = int(sum(progress_list) / len(progress_list)) if progress_list else 0

        module_summary.append({
            'name': module.name,
            'session_count': module_sessions.count(),
            'time_spent_minutes': time_spent_minutes,
            'average_progress': avg_progress,
        })

    # Recent sessions and top modules
    recent_sessions = sessions.order_by('-check_in')[:10]
    top_modules = (
        sessions.filter(module__isnull=False)
        .values('module__name')
        .annotate(avg_progress=Avg('progress'), session_count=Count('id'))
        .order_by('-session_count')[:3]
    )

    # Admin messages
    messages_list = AdminMessage.objects.order_by('-timestamp')[:5]
    unread_count = AdminMessage.objects.filter(is_read=False).count()

    return render(request, 'student_panel/dashboard.html', {
        'student': student,
        'greeting': greeting,
        'total_modules': total_modules,
        'completed_modules': completed_modules,
        'remaining_modules': remaining_modules,
        'total_hours': hours,
        'total_minutes': minutes,
        'most_used_module': most_used_module,
        'completion_percent': completion_percent,
        'remaining_percent': remaining_percent,
        'labels': json.dumps(labels),
        'monthly_progress': json.dumps(monthly_progress),
        'monthly_usage_percentage': json.dumps(monthly_usage_percentage),
        'trend_percent': abs(change_percent),
        'trend_class': trend_class,
        'trend_icon': trend_icon,
        'trend_label': labels[-1].split(" ")[-1],
        'module_summary': module_summary,
        'recent_sessions': recent_sessions,
        'top_modules': top_modules,
        'messages': messages_list,
        'unread_count': unread_count,
    })
