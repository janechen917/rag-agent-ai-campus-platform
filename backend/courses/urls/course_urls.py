from django.urls import path, include
from rest_framework.routers import DefaultRouter
from courses.views import CourseViewSet, EnrollmentViewSet, ReviewViewSet, CourseRequestViewSet

router = DefaultRouter()
router.register(r'course', CourseViewSet, basename='course')
router.register(r'course-enrollments', EnrollmentViewSet, basename='course-enrollment')
router.register(r'course-reviews', ReviewViewSet, basename='course-review')
router.register(r'course-requests', CourseRequestViewSet, basename='course-request')

urlpatterns = router.urls
