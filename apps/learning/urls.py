from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LearningPathViewSet, ModuleViewSet, ContentViewSet, UserProgressViewSet, ConceptViewSet

router = DefaultRouter()
router.register(r'paths', LearningPathViewSet, basename='learningpath')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'contents', ContentViewSet, basename='content')
router.register(r'progress', UserProgressViewSet, basename='userprogress')
router.register(r'concepts', ConceptViewSet, basename='concept')

urlpatterns = [
    path('', include(router.urls)),
]

