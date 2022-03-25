# -*- coding: utf-8
from rest_framework import routers

from .views import SchoolViewSet, TeacherViewSet

router = routers.SimpleRouter()
router.register("teachers", TeacherViewSet)
router.register("schools", SchoolViewSet)

urlpatterns = router.urls
