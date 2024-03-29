#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_drf-dynamic-fields
-----------

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
        request = rf.get("/api/v1/schools/1/?fields=id")
        serializer = TeacherSerializer(context={"request": request})

        self.assertEqual(set(serializer.fields.keys()), set(("id",)))

    def test_fields_left_alone(self):
        """
        What if no fields param is passed? It should not touch the fields.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/")
        serializer = TeacherSerializer(context={"request": request})

        self.assertEqual(
            set(serializer.fields.keys()), set(("id", "request_info", "age", "name"))
        )

    def test_fields_all_gone(self):
        """
        If we pass a blank fields list, then no fields should return.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?fields")
        serializer = TeacherSerializer(context={"request": request})

        self.assertEqual(set(serializer.fields.keys()), set())

    def test_ordinary_serializer(self):
        """
        Check the full JSON output of the serializer.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?fields=id,age")
        teacher = Teacher.objects.create(name="Susan", age=34)

        serializer = TeacherSerializer(teacher, context={"request": request})

        self.assertEqual(serializer.data, {"id": teacher.id, "age": teacher.age})

    def test_omit(self):
        """
        Check a basic usage of omit.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?omit=request_info")
        serializer = TeacherSerializer(context={"request": request})

        self.assertEqual(set(serializer.fields.keys()), set(("id", "name", "age")))

    def test_omit_and_fields_used(self):
        """
        Can they be used together.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?fields=id,request_info&omit=request_info")
        serializer = TeacherSerializer(context={"request": request})

        self.assertEqual(set(serializer.fields.keys()), set(("id",)))

    def test_omit_everything(self):
        """
        Can remove it all tediously.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?omit=id,request_info,age,name")
        serializer = TeacherSerializer(context={"request": request})

        self.assertEqual(set(serializer.fields.keys()), set())

    def test_omit_nothing(self):
        """
        Blank omit doesn't affect anything.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?omit")
        serializer = TeacherSerializer(context={"request": request})

        self.assertEqual(
            set(serializer.fields.keys()), set(("id", "request_info", "name", "age"))
        )

    def test_omit_non_existant_field(self):
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?omit=pretend")
        serializer = TeacherSerializer(context={"request": request})

        self.assertEqual(
            set(serializer.fields.keys()), set(("id", "request_info", "name", "age"))
        )

    def test_as_nested_serializer(self):
        """
        Nested serializers are not filtered.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?fields=teachers")

        school = School.objects.create(name="Python Heights High")
        teachers = [
            Teacher.objects.create(name="Shane", age=45),
            Teacher.objects.create(name="Kaz", age=29),
        ]
        school.teachers.add(*teachers)

        serializer = SchoolSerializer(school, context={"request": request})

        request_info = "http://testserver/api/v1/teacher/{}"

        self.assertEqual(
            serializer.data,
            {
                "teachers": [
                    OrderedDict(
                        [
                            ("id", teachers[0].id),
                            ("request_info", request_info.format(teachers[0].id)),
                            ("age", teachers[0].age),
                            ("name", teachers[0].name),
                        ]
                    ),
                    OrderedDict(
                        [
                            ("id", teachers[1].id),
                            ("request_info", request_info.format(teachers[1].id)),
                            ("age", teachers[1].age),
                            ("name", teachers[1].name),
                        ]
                    ),
                ],
            },
        )

    def test_serializer_reuse_with_changing_request(self):
        """
        `fields` is a cached property. Changing the request on an already
        instantiated serializer will not result in a changed fields attribute.

        This was a deliberate choice we have made in favor of speeding up
        access to the slow `fields` attribute.
        """

        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?fields=id")
        serializer = TeacherSerializer(context={"request": request})
        self.assertEqual(set(serializer.fields.keys()), {"id"})

        # now change the request on this instantiated serializer.
        request2 = rf.get("/api/v1/schools/1/?fields=id,name")
        serializer.context["request"] = request2
        self.assertEqual(set(serializer.fields.keys()), {"id"})
