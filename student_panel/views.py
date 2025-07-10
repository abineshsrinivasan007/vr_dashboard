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



# students/views.py
from django.shortcuts import render, redirect
from students.models import Student
from datetime import datetime

def student_dashboard(request):
    if 'student_id' not in request.session:
        return redirect('student_login')

    student = Student.objects.select_related('degree', 'department', 'section').get(id=request.session['student_id'])
    
    # Greeting based on time
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    print("Student:", student.name)
    print("Degree:", student.degree.name)
    

    return render(request, 'student_panel/dashboard.html', {
        'student': student,
        'greeting': greeting,
    })
