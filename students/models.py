from django.db import models
from django.utils import timezone

class Degree(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Department(models.Model):
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.degree.name} - {self.name}"

class Section(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    section = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.department} - {self.section}"

class Student(models.Model):
    name = models.CharField(max_length=100)
    degree = models.ForeignKey(Degree, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True,default=1)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    vp_code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    

    def __str__(self):
        return self.name

class Module(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Session(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    check_in = models.DateTimeField(auto_now_add=True)
    check_out = models.DateTimeField(null=True, blank=True)
    progress = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student.name} - {self.module.name}"

# students/models.py
from django.db import models
from django.contrib.auth.hashers import make_password

class AdminUser(models.Model):
    name = models.CharField(max_length=100)
    staff_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)  # Optional email field
    password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        # Hash the password if not already hashed
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.staff_id} - {self.name}"





from django.db import models

class AdminMessage(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) 
    def __str__(self):
        return self.message[:50]
