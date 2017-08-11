"""
Some models for the tests. We are modelling a school.
"""
from django.db import models


class Pet(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()


class Teacher(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    class_pet = models.ForeignKey(Pet, blank=True, null=True)


class School(models.Model):
    """Schools just have teachers, no students."""
    teachers = models.ManyToManyField(Teacher)
