from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
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
