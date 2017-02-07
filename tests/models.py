from django.db import models


class Teacher(models.Model):
    pass


class School(models.Model):
    teachers = models.ManyToManyField(Teacher)
