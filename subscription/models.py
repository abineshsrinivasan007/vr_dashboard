from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
class Feature(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
class Plan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_months = models.PositiveIntegerField(default=1)   # 👈 ADD THIS
    max_students = models.IntegerField()
    max_staff = models.IntegerField()
    is_popular = models.BooleanField(default=False)
    features = models.ManyToManyField(Feature, blank=True)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    college_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # hashed in production
    phone = models.CharField(max_length=15, blank=True, null=True)  # ✅ Add this
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    students_count = models.PositiveIntegerField(default=0)
    staff_count = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=30*self.plan.duration_months)
        super().save(*args, **kwargs)
