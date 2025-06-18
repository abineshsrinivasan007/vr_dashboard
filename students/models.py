from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True) 
    vp_code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
class Module(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Session(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    check_in = models.DateTimeField(auto_now_add=True)
    check_out = models.DateTimeField(null=True, blank=True)
    progress = models.IntegerField(default=0)  # Percentage 0-100

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
