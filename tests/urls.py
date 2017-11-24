# -*- coding: utf-8

from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('teachers', views.TeacherViewSet)
router.register('schools', views.SchoolViewSet)

urlpatterns = [
    url(r'^api/v1/', include(router.urls)),
]
