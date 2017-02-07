from django.db import models

from rest_framework import serializers

from drf_dynamic_fields import DynamicFieldsMixin

from .models import Teacher, School


class TeacherSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    request_info = serializers.SerializerMethodField()
    class Meta:
        model = Teacher
        fields = ('id', 'request_info')

    def get_request_info(self, teacher):
        """
        a meaningless method that attempts
        to access the request object.
        """
        request = self.context['request']
        return request.build_absolute_uri(
            '/api/v1/teacher/{}'.format(teacher.pk)
        )


class SchoolSerializer(serializers.ModelSerializer):

    teachers = TeacherSerializer(many=True, read_only=True)

    class Meta:
        model = School
        fields = ('id', 'teachers')
