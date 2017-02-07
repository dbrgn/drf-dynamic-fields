#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_drf-dynamic-fields
------------

Tests for `drf-dynamic-fields` mixins
"""
from collections import OrderedDict

from django.test import TestCase, RequestFactory
from drf_dynamic_fields import DynamicFieldsMixin

from .serializers import SchoolSerializer, TeacherSerializer
from .models import Teacher, School


class TestDynamicFieldsMixin(TestCase):

    def test_removes_fields(self):
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?fields=id')
        serializer = TeacherSerializer(context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set(('id',))
        )

    def test_fields_left_alone(self):
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/')
        serializer = TeacherSerializer(context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set(('id', 'request_info'))
        )

    def test_ordinary_serializer(self):
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?fields=id')
        teacher = Teacher.objects.create()

        serializer = TeacherSerializer(teacher, context={'request': request})

        self.assertEqual(
            serializer.data, {
                'id': teacher.id
            }
        )

    def test_as_nested_serializer(self):

        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/')

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
                        ('request_info', request_info.format(teachers[0].id))
                    ]),
                    OrderedDict([
                        ('id', teachers[1].id),
                        ('request_info', request_info.format(teachers[1].id))
                    ])
                ],
                'id': school.id
            }
        )
