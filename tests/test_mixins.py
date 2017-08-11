#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_drf-dynamic-fields
------------

Tests for `drf-dynamic-fields` mixins
"""
from collections import OrderedDict

from django.test import TestCase, RequestFactory

from .serializers import SchoolSerializer, TeacherSerializer
from .models import Teacher, School, Pet


class TestDynamicFieldsMixin(TestCase):
    """
    Test case for the DynamicFieldsMixin
    """

    def test_removes_fields(self):
        """
        Does it actually remove fields?
        """
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?fields=id')
        serializer = TeacherSerializer(context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set(('id',))
        )

    def test_fields_left_alone(self):
        """
        What if no fields param is passed? It should not touch the fields.
        """
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/')
        serializer = TeacherSerializer(context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set(('id', 'request_info', 'name', 'class_pet'))
        )

    def test_fields_all_gone(self):
        """
        If we pass a blank fields list, then no fields should return.
        """
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?fields')
        serializer = TeacherSerializer(context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set()
        )

    def test_ordinary_serializer(self):
        """
        Check the full JSON output of the serializer.
        """
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?fields=id')
        teacher = Teacher.objects.create()

        serializer = TeacherSerializer(teacher, context={'request': request})

        self.assertEqual(
            serializer.data, {
                'id': teacher.id
            }
        )

    def test_omit(self):
        """
        Check a basic usage of omit.
        """
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?omit=request_info,class_pet')
        serializer = TeacherSerializer(context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set(('id', 'name'))
        )

    def test_omit_and_fields_used(self):
        """
        Can they be used together.
        """
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?fields=id,request_info&omit=request_info')
        serializer = TeacherSerializer(context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set(('id',))
        )

    def test_omit_everything(self):
        """
        Can remove it all tediously.
        """
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?omit=id,name,request_info,class_pet')
        serializer = TeacherSerializer(context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set()
        )

    def test_omit_nothing(self):
        """
        Blank omit doesn't affect anything.
        """
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?omit')
        serializer = TeacherSerializer(context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set(('id', 'request_info', 'name', 'class_pet'))
        )

    def test_omit_non_existant_field(self):
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?omit=pretend')
        serializer = TeacherSerializer(context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set(('id', 'request_info', 'name', 'class_pet'))
        )

    def test_as_nested_serializer(self):
        """
        Nested serializers are not filtered, without nested filter paths
        """
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?fields=teachers')

        school = School.objects.create()
        teachers = [
            Teacher.objects.create(),
            Teacher.objects.create()
        ]
        school.teachers.add(*teachers)

        serializer = SchoolSerializer(school, context={'request': request})

        request_info = 'http://testserver/api/v1/teacher/{}'

        self.assertEqual(
            serializer.data, {
                'teachers': [
                    OrderedDict([
                        ('id', teachers[0].id),
                        ('name', teachers[0].name),
                        ('request_info', request_info.format(teachers[0].id)),
                        ('class_pet', None),
                    ]),
                    OrderedDict([
                        ('id', teachers[1].id),
                        ('name', teachers[1].name),
                        ('request_info', request_info.format(teachers[1].id)),
                        ('class_pet', None),
                    ])
                ],
            }
        )

    def test_as_nested_serializer_list_with_filter(self):
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?fields=teachers__id,teachers__class_pet__name')

        pet = Pet.objects.create(name="Hamster", age=1)
        school = School.objects.create()
        teachers = [
            Teacher.objects.create(class_pet=pet),
            Teacher.objects.create()
        ]
        school.teachers.add(*teachers)

        serializer = SchoolSerializer(school, context={'request': request})

        self.assertEqual(
            serializer.data, {
                'teachers': [
                    OrderedDict([
                        ('id', teachers[0].id),
                        ('class_pet', OrderedDict([('name', pet.name)])),
                    ]),
                    OrderedDict([
                        ('id', teachers[1].id),
                        ('class_pet', None),
                    ])
                ],
            }
        )

    def test_as_nested_serializer_list_with_omit(self):
        """
        Nested serializers are not filtered, without nested filter paths
        """
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?omit=teachers__id,teachers__class_pet__id,teachers__class_pet__age')

        pet = Pet.objects.create(name="Hamster", age=1)
        school = School.objects.create()
        teachers = [
            Teacher.objects.create(class_pet=pet),
            Teacher.objects.create()
        ]
        school.teachers.add(*teachers)

        serializer = SchoolSerializer(school, context={'request': request})

        request_info = 'http://testserver/api/v1/teacher/{}'

        self.assertEqual(
            serializer.data, {
                'id': school.id,
                'teachers': [
                    OrderedDict([
                        ('name', teachers[0].name),
                        ('request_info', request_info.format(teachers[0].id)),
                        ('class_pet', OrderedDict([('name', pet.name)])),
                    ]),
                    OrderedDict([
                        ('name', teachers[1].name),
                        ('request_info', request_info.format(teachers[1].id)),
                        ('class_pet', None),
                    ])
                ],
            }
        )

    def test_with_nested_field_limiting(self):
        rf = RequestFactory()
        request = rf.get('/api/v1/teacher/1/?fields=id,name,class_pet__age')

        pet = Pet.objects.create(name="Hamster", age=2)
        teacher = Teacher.objects.create(name="Dr. Smith", class_pet=pet)

        serializer = TeacherSerializer(teacher, context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set(('id', 'name', 'class_pet'))
        )

        self.assertEqual(
            serializer.data, {
                'id': teacher.id,
                'name': teacher.name,
                'class_pet': OrderedDict([('age', pet.age)])
            }
        )

    def test_with_nested_field_omitting(self):
        rf = RequestFactory()
        request = rf.get('/api/v1/teacher/1/?omit=name,request_info,class_pet__age')

        pet = Pet.objects.create(name="Hamster", age=2)
        teacher = Teacher.objects.create(name="Dr. Smith", class_pet=pet)

        serializer = TeacherSerializer(teacher, context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set(('id', 'class_pet'))
        )

        self.assertEqual(
            serializer.data, {
                'id': teacher.id,
                'class_pet': OrderedDict([('id', pet.id), ('name', pet.name)])
            }
        )