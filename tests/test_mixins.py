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

from .serializers import SchoolSerializer
from .models import Teacher, School


class TestDynamicFieldsMixin(TestCase):

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



