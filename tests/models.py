"""
Some models for the tests. We are modelling a school.
"""
from django.db import models


class Teacher(models.Model):
    name = models.CharField(max_length=30)
    age = models.IntegerField()


class School(models.Model):
    """Schools just have teachers, no students."""

    name = models.CharField(max_length=30)
    teachers = models.ManyToManyField(Teacher)
