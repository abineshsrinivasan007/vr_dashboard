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



def student_dashboard(request):
    if 'student_id' not in request.session:
        return redirect('student_login')

    from students.models import Session, Module, Student, AdminMessage
    from django.utils import timezone
    from datetime import datetime
    from django.utils.timezone import now
    from django.db.models import Count
    from dateutil.relativedelta import relativedelta
    import json
    from django.db.models import Avg, Count


    student = Student.objects.get(id=request.session['student_id'])

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

    # Time spent
    sessions = Session.objects.filter(student=student)
    total_seconds = sum([(s.check_out - s.check_in).total_seconds() for s in sessions if s.check_out], 0)
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    total_minutes = minutes % 60
    total_hours = hours // 60

    # Most used module
    most_used = (
        Session.objects.filter(student=student)
        .values('module__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )
    most_used_module = most_used['module__name'] if most_used else "N/A"
    completion_percent = int((completed_modules / total_modules) * 100) if total_modules else 0
    remaining_percent = 100 - completion_percent

    # === Monthly Completion Graph Data ===
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
            check_out__month=month,
        ).values('module').distinct().count()

        accessed = Session.objects.filter(
            student=student,
            check_out__year=year,
            check_out__month=month,
        ).values('module').distinct().count()

        labels.append(month_date.strftime('%b %Y'))
        monthly_progress.append(completed)

        percentage = int((completed / accessed) * 100) if accessed else 0
        monthly_usage_percentage.append(percentage)

    # === Calculate Dynamic Percentage Change (Based on Completions) ===
    if len(monthly_progress) >= 2:
        current = monthly_progress[-1]
        previous = monthly_progress[-2]

        if previous > 0:
            change_percent = round(((current - previous) / previous) * 100)
        else:
            change_percent = 100 if current > 0 else 0
    else:
        change_percent = 0

    trend_direction = "up" if change_percent >= 0 else "down"
    trend_class = "text-success" if change_percent >= 0 else "text-danger"
    trend_icon = "fa-arrow-up" if change_percent >= 0 else "fa-arrow-down"
    # === Dynamic Module Data: Sessions, Time Spent, Progress ===
    module_summary = []

    student_modules = (
        Session.objects.filter(student=student)
        .values('module')
        .distinct()
            )

    for entry in student_modules:
        module_id = entry['module']
        module = Module.objects.get(id=module_id)
        module_sessions = sessions.filter(module=module)

        total_time = sum(
        [(s.check_out - s.check_in).total_seconds() for s in module_sessions if s.check_out],
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
        
        recent_sessions = Session.objects.filter(student=student).order_by('-check_in')[:10]
       
        top_modules = (
        Session.objects.filter(student=student)
        .values('module__name')
        .annotate(avg_progress=Avg('progress'), session_count=Count('id'))
        .order_by('-session_count')[:3]
    )
    messages = AdminMessage.objects.order_by('-timestamp')[:5]
    print("Messages:", messages)
    return render(request, 'student_panel/dashboard.html', {
        'student': student,
        'greeting': greeting,
        'total_modules': total_modules,
        'completed_modules': completed_modules,
        'remaining_modules': remaining_modules,
        'total_hours': hours,
        'total_minutes': minutes,
        'hours': total_hours,
        'minutes': total_minutes,
        'most_used_module': most_used_module,
        'completion_percent': completion_percent,
        'remaining_percent': remaining_percent,

        # For chart.js
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
        'messages': messages

    })


from django.shortcuts import redirect
from django.contrib import messages

def student_logout(request):
    if 'student_user_id' not in request.session:
        messages.error(request, "You are not logged in.")
        return redirect('student_login')
    request.session.flush()  # ✅ Clears session data
    messages.success(request, "You have successfully logged out.")
    return redirect('student_login')  # Replace with your actual login URL name