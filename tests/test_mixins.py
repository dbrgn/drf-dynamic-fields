#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_drf-dynamic-fields
-----------

Tests for `drf-dynamic-fields` mixins
"""
from collections import OrderedDict

from django.test import TestCase, RequestFactory

from .serializers import (
    NestableSchoolSerializer,
    NestableTeacherSerializer,
    SchoolSerializer,
    TeacherSerializer,
    ParentSerializer,
)
from .models import Teacher, School, Child, Parent


class TestDynamicFieldsMixin(TestCase):
    """
    Test case for the DynamicFieldsMixin
    """

    SchoolSerializer = SchoolSerializer
    TeacherSerializer = TeacherSerializer

    def test_removes_fields(self):
        """
        Does it actually remove fields?
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?fields=id")
        serializer = self.TeacherSerializer(context={"request": request})

        self.assertEqual(set(serializer.fields.keys()), set(("id",)))

    def test_fields_left_alone(self):
        """
        What if no fields param is passed? It should not touch the fields.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/")
        serializer = self.TeacherSerializer(context={"request": request})

        self.assertEqual(
            set(serializer.fields.keys()), set(("id", "request_info", "age", "name"))
        )

    def test_fields_all_gone(self):
        """
        If we pass a blank fields list, then no fields should return.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?fields")
        serializer = self.TeacherSerializer(context={"request": request})

        self.assertEqual(set(serializer.fields.keys()), set())

    def test_ordinary_serializer(self):
        """
        Check the full JSON output of the serializer.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?fields=id,age")
        teacher = Teacher.objects.create(name="Susan", age=34)

        serializer = self.TeacherSerializer(teacher, context={"request": request})

        self.assertEqual(serializer.data, {"id": teacher.id, "age": teacher.age})

    def test_omit(self):
        """
        Check a basic usage of omit.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?omit=request_info")
        serializer = self.TeacherSerializer(context={"request": request})

        self.assertEqual(set(serializer.fields.keys()), set(("id", "name", "age")))

    def test_omit_and_fields_used(self):
        """
        Can they be used together.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?fields=id,request_info&omit=request_info")
        serializer = self.TeacherSerializer(context={"request": request})

        self.assertEqual(set(serializer.fields.keys()), set(("id",)))

    def test_omit_everything(self):
        """
        Can remove it all tediously.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?omit=id,request_info,age,name")
        serializer = self.TeacherSerializer(context={"request": request})

        self.assertEqual(set(serializer.fields.keys()), set())

    def test_omit_nothing(self):
        """
        Blank omit doesn't affect anything.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?omit")
        serializer = self.TeacherSerializer(context={"request": request})

        self.assertEqual(
            set(serializer.fields.keys()), set(("id", "request_info", "name", "age"))
        )

    def test_omit_non_existant_field(self):
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?omit=pretend")
        serializer = self.TeacherSerializer(context={"request": request})

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

        serializer = self.SchoolSerializer(school, context={"request": request})

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
        serializer = self.TeacherSerializer(context={"request": request})
        self.assertEqual(set(serializer.fields.keys()), {"id"})

        # now change the request on this instantiated serializer.
        request2 = rf.get("/api/v1/schools/1/?fields=id,name")
        serializer.context["request"] = request2
        self.assertEqual(set(serializer.fields.keys()), {"id"})

class TestNestedDynamicFieldsMixin(TestDynamicFieldsMixin):
    """
    Test case for the NestedDynamicFieldsMixin
    """
    SchoolSerializer = NestableSchoolSerializer
    TeacherSerializer = NestableTeacherSerializer

    def _assert_nested_fields(self, data, expected_fields):
        """
        Assert nested fields match the expected fields.
        """
        for parent, nested_fields in expected_fields.items():
            with self.subTest(parent=parent):
                items = data[parent]
                if nested_fields is None:
                    continue
                expected_set = set(nested_fields)
                for obj in items:
                    with self.subTest(parent=parent):
                        actual_set = set(obj.keys())
                        self.assertEqual(
                            actual_set,
                            expected_set,
                            f"{parent} fields mismatch: expected "
                            f"exactly {nested_fields}, got {list(obj.keys())}",
                        )

    @staticmethod
    def _prepare_school_instance():
        """Prepare school instance for testing."""
        school = School.objects.create(name="Python Heights High")
        teachers = [
            Teacher.objects.create(name="Shane", age=45),
            Teacher.objects.create(name="Kaz", age=29),
        ]
        school.teachers.add(*teachers)
        return school

    def test_omit_nested_field(self):
        """Omitting a nested field"""
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?omit=invalid,name,teachers__age,teachers__invalid")

        school = self._prepare_school_instance()
        serializer = self.SchoolSerializer(school, context={"request": request})
        data = serializer.data

        # Confirm omitted fields are in deferred list
        deferred = set(serializer.get_model_fields_to_defer())
        self.assertEqual({"name", "teachers__age"}, deferred)

        expected_fields = {"id": None, "teachers": ["id", "name", "request_info"]}
        # Assert top‐level keys exactly match
        self.assertEqual(set(data.keys()), set(expected_fields.keys()))

        # Assert nested fields.
        self._assert_nested_fields(data, expected_fields)

    def test_omit_everything_nested_field(self):
        """Omitting all fields within a nested field"""
        rf = RequestFactory()
        request = rf.get(
            "/api/v1/schools/1/?omit=teachers__id,teachers__age,teachers__name,teachers__request_info"
        )

        school = self._prepare_school_instance()
        serializer = self.SchoolSerializer(school, context={"request": request})
        data = serializer.data

        expected_fields = {"id": None, "name": None, "teachers": []}
        # Assert top‐level keys exactly match
        self.assertEqual(set(data.keys()), set(expected_fields.keys()))

        # Assert nested fields.
        self._assert_nested_fields(data, expected_fields)

    def test_omit_top_field_and_keep_all_nested_fields(self):
        """Omitting a top-level field while keeping all nested fields"""
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?omit=name")

        school = self._prepare_school_instance()
        serializer = self.SchoolSerializer(school, context={"request": request})
        data = serializer.data

        expected_fields = {
            "id": None,
            "teachers": ["id", "name", "request_info", "age"],
        }
        # Assert top‐level keys exactly match
        self.assertEqual(set(data.keys()), set(expected_fields.keys()))

        # Assert nested fields.
        self._assert_nested_fields(data, expected_fields)

    def test_allow_nested_field(self):
        """Select only the requested fields, including nested-level fields."""
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?fields=invalid,id,teachers__age,teachers__invalid")
        school = self._prepare_school_instance()
        serializer = self.SchoolSerializer(school, context={"request": request})

        # Confirm omitted fields are in deferred list
        deferred = set(serializer.get_model_fields_to_defer())
        self.assertEqual({"name","teachers__name", "teachers__id"}, deferred)

        data = serializer.data
        expected_fields = {"id": None, "teachers": ["age"]}
        # Assert top‐level keys exactly match
        self.assertEqual(set(data.keys()), set(expected_fields.keys()))

        # Assert nested fields.
        self._assert_nested_fields(data, expected_fields)

    def test_fields_all_gone_nested(self):
        """If no fields are selected, all fields are omitted, including those
        from the nested serializer.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?fields")
        school = self._prepare_school_instance()
        serializer = self.SchoolSerializer(school, context={"request": request})

        data = serializer.data
        expected_fields = {}
        # Assert top‐level keys exactly match
        self.assertEqual(set(data.keys()), set(expected_fields.keys()))

        # Assert nested fields.
        self._assert_nested_fields(data, expected_fields)

    def test_nested_omit_and_fields_used(self):
        """Omit and fields can be used together at the nested field level."""
        rf = RequestFactory()
        request = rf.get(
            "/api/v1/schools/1/?fields=id,name,teachers__name,teachers__age&omit=name,teachers__name"
        )
        school = self._prepare_school_instance()
        serializer = self.SchoolSerializer(school, context={"request": request})

        data = serializer.data
        expected_fields = {"id": None, "teachers": ["age"]}
        # Assert top‐level keys exactly match
        self.assertEqual(set(data.keys()), set(expected_fields.keys()))

        # Assert nested fields.
        self._assert_nested_fields(data, expected_fields)

    def test_omit_nothing_nested(self):
        """
        Blank omit doesn't affect nested fields.
        """
        rf = RequestFactory()
        request = rf.get("/api/v1/schools/1/?omit")
        school = self._prepare_school_instance()
        serializer = self.SchoolSerializer(school, context={"request": request})

        data = serializer.data
        expected_fields = {
            "id": None,
            "name": None,
            "teachers": ["id", "age", "name", "request_info"],
        }
        # Assert top‐level keys exactly match
        self.assertEqual(set(data.keys()), set(expected_fields.keys()))

        # Assert nested fields.
        self._assert_nested_fields(data, expected_fields)

    def test_single_nested_instance_omit_field(self):
        """Omit also works for filtering fields on single nested instances"""
        child = Child(secret="secret_key", public="public_key")
        parent = Parent(id=1, child=child)
        rf = RequestFactory()
        request = rf.get("/api/v1/parent/1/?omit=id,child__secret")
        serializer = ParentSerializer(parent, context={"request": request})
        data = serializer.data

        self.assertNotIn("id", data)
        self.assertNotIn("secret", data["child"])
        self.assertEqual(data["child"]["public"], "public_key")

    def test_single_nested_instance_allow_field(self):
        """Fields selection also works for filtering fields on single nested instances"""
        child = Child(secret="secret_key", public="public_key")
        parent = Parent(id=1, child=child)
        rf = RequestFactory()
        request = rf.get("/api/v1/parent/1/?fields=id,child__secret")
        serializer = ParentSerializer(parent, context={"request": request})
        data = serializer.data

        self.assertEqual(data["id"], 1)
        self.assertIn("secret", data["child"])
        self.assertEqual(data["child"]["secret"], "secret_key")
        self.assertNotIn("public", data["child"])


