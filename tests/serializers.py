"""
For the tests.
"""
from rest_framework import serializers

from drf_dynamic_fields import DynamicFieldsMixin

from .models import Teacher, School, Pet


class PetSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ('id', 'name', 'age')


class TeacherSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """
    The request_info field is to highlight the issue accessing request during
    a nested serializer.
    """

    request_info = serializers.SerializerMethodField()
    class_pet = PetSerializer()

    class Meta:
        model = Teacher
        fields = ('id', 'name', 'request_info', 'class_pet',)

    def get_request_info(self, teacher):
        """
        a meaningless method that attempts
        to access the request object.
        """
        request = self.context['request']
        return request.build_absolute_uri(
            '/api/v1/teacher/{}'.format(teacher.pk)
        )


class SchoolSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    """
    Interesting enough serializer because the TeacherSerializer
    will use ListSerializer due to the `many=True`
    """

    teachers = TeacherSerializer(many=True, read_only=True)

    class Meta:
        model = School
        fields = ('id', 'teachers')
