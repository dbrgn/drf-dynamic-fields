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
from .models import Teacher, School


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
            set(('id', 'request_info'))
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
        request = rf.get('/api/v1/schools/1/?omit=request_info')
        serializer = TeacherSerializer(context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set(('id',))
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
        request = rf.get('/api/v1/schools/1/?omit=id,request_info')
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
            set(('id', 'request_info'))
        )

    def test_omit_non_existant_field(self):
        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/?omit=pretend')
        serializer = TeacherSerializer(context={'request': request})

        self.assertEqual(
            set(serializer.fields.keys()),
            set(('id', 'request_info'))
        )

    def test_as_nested_serializer(self):
        """
        Nested serializers are not filtered.
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
                        ('request_info', request_info.format(teachers[0].id))
                    ]),
                    OrderedDict([
                        ('id', teachers[1].id),
                        ('request_info', request_info.format(teachers[1].id))
                    ])
                ],
            }
        )
