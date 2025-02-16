# Thirdparty imports
from django.urls import path
from rest_framework.routers import DefaultRouter

# Projects imports
from .views import ShopUserViewSet

router = DefaultRouter()
router.register(
    r'users',
    ShopUserViewSet,
    basename='users_create_v1'
)

urlpatterns = router.urls
