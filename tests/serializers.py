"""
For the tests.
"""
from rest_framework import serializers

from drf_dynamic_fields import DynamicFieldsMixin, NestedDynamicFieldsMixin

from .models import Teacher, School, Child


class BaseTeacherSerializer(serializers.ModelSerializer):

    request_info = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ("id", "request_info", "age", "name")

    def get_request_info(self, teacher):
        """
        a meaningless method that attempts
        to access the request object.
        """
        request = self.context["request"]
        return request.build_absolute_uri("/api/v1/teacher/{}".format(teacher.pk))


class TeacherSerializer(DynamicFieldsMixin, BaseTeacherSerializer):
    pass


class NestableTeacherSerializer(NestedDynamicFieldsMixin, BaseTeacherSerializer):
    """
    The request_info field is to highlight the issue accessing request during
    a nested serializer.

    """

class BaseSchoolSerializer(serializers.ModelSerializer):


    class Meta:
        model = School
        fields = ("id", "teachers", "name")


class SchoolSerializer(DynamicFieldsMixin, BaseSchoolSerializer):
    teachers = TeacherSerializer(many=True, read_only=True)


class NestableSchoolSerializer(NestedDynamicFieldsMixin, BaseSchoolSerializer):
    """
    Interesting enough serializer because the TeacherSerializer
    will use ListSerializer due to the `many=True`
    """
    teachers = NestableTeacherSerializer(many=True, read_only=True)

class ChildSerializer(NestedDynamicFieldsMixin, serializers.Serializer):
    secret = serializers.CharField()
    public = serializers.CharField()

    class Meta:
        model = Child


class ParentSerializer(NestedDynamicFieldsMixin, serializers.Serializer):
    id = serializers.IntegerField()
    child = ChildSerializer()
