from rest_framework.views import APIView
from rest_framework.response import Response
from students.models import Student

class LoginView(APIView):
    def post(self, request):
        vp_code = request.data.get('vp_code')
        if not vp_code:
            return Response({"error": "VP code is required"}, status=400)
        try:
            student = Student.objects.get(vp_code=vp_code)
            return Response({
                "id": student.id,
                "name": student.name
            })
        except Student.DoesNotExist:
            return Response({"error": "Invalid VP code"}, status=400)
        

        
from students.models import Module, Session
from django.utils import timezone

class StartSessionView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        module_id = request.data.get('module_id')
        session = Session.objects.create(
            student_id=student_id,
            module_id=module_id,
            check_in=timezone.now()
        )
        return Response({"session_id": session.id,
                         "message": "Session started" })

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
