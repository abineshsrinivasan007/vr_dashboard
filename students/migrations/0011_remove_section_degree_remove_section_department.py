# Generated by Django 5.2.2 on 2025-06-23 06:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0010_student_degree_student_department_student_section'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='section',
            name='Degree',
        ),
        migrations.RemoveField(
            model_name='section',
            name='department',
        ),
    ]
