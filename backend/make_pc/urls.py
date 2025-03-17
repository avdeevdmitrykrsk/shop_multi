# Thirdparty imports
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Projects imports
from make_pc.views import MakePcViewSet

router = DefaultRouter()
router.register(r'make_pc', MakePcViewSet, basename='make_pc_v1')

urlpatterns = [
    path('', include(router.urls)),
]
