from rest_framework.viewsets import ModelViewSet

from .models import School, Teacher
from .serializers import SchoolSerializer, TeacherSerializer


class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class SchoolViewSet(ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
