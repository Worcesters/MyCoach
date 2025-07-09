from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MachineViewSet, MuscleGroupViewSet, LabelViewSet, MachineRatingViewSet

router = DefaultRouter()
router.register(r'machines', MachineViewSet)
router.register(r'muscle-groups', MuscleGroupViewSet)
router.register(r'labels', LabelViewSet)
router.register(r'ratings', MachineRatingViewSet)

app_name = 'machines'

urlpatterns = [
    path('', include(router.urls)),
]