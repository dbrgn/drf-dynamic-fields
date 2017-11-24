"""
Some models for the tests. We are modelling a school.
"""
from django.db import models


class Teacher(models.Model):
    name = models.CharField(max_length=200)


class School(models.Model):
    """Schools just have teachers, no students."""
    teachers = models.ManyToManyField(Teacher)
