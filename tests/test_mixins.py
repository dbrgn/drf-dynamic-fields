#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_drf-dynamic-fields
------------

Tests for `drf-dynamic-fields` mixins
"""

from django.test import TestCase, RequestFactory
from drf_dynamic_fields import DynamicFieldsMixin

from .serializers import SchoolSerializer
from .models import Teacher, School


class TestDynamicFieldsMixin(TestCase):

    def test_as_nested_serializer(self):

        rf = RequestFactory()
        request = rf.get('/api/v1/schools/1/')

        school = School.objects.create()
        school.teachers.add(
            Teacher.objects.create(),
            Teacher.objects.create()
        )

        serializer = SchoolSerializer(school, context={'request': request})

        self.assertEqual(
            serializer.data, {
            }
        )



