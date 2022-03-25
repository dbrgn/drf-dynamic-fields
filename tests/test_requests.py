#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_drf-dynamic-fields
------------

Test for the full request cycle using dynamic fields mixns
"""
from collections import OrderedDict

from django.test import TestCase, RequestFactory

from rest_framework.reverse import reverse

from .serializers import SchoolSerializer, TeacherSerializer
from .models import Teacher, School


class TestDynamicFieldsViews(TestCase):
    """
    Testing using dynamic fields in request framework views.
    """

    def setUp(self):
        """
        Create some teachers and schools.
        """
        teachers = [("Craig", 34), ("Kaz", 29), ("Sun", 62)]

        schools = ["Python Heights High", "Ruby Consolidated", "Java Coffee School"]

        t = [Teacher.objects.create(name=name, age=age) for name, age in teachers]

        for name in schools:
            s = School.objects.create(name=name)
            s.teachers.add(*t)

    def test_teacher_basic(self):

        response = self.client.get(reverse("teacher-list"))
        for teacher in response.data:
            self.assertEqual(teacher.keys(), {"id", "request_info", "age", "name"})

    def test_teacher_fields(self):

        response = self.client.get(reverse("teacher-list"), {"fields": "id,age"})
        for teacher in response.data:
            self.assertEqual(teacher.keys(), {"id", "age"})

    def test_teacher_omit(self):

        response = self.client.get(reverse("teacher-list"), {"omit": "id,age"})
        for teacher in response.data:
            self.assertEqual(teacher.keys(), {"request_info", "name"})

    def test_nested_teacher_fields(self):

        response = self.client.get(reverse("school-list"), {"fields": "name,teachers"})
        for school in response.data:
            self.assertEqual(school.keys(), {"teachers", "name"})
            self.assertEqual(
                school["teachers"][0].keys(), {"id", "request_info", "age", "name"}
            )
