# Thirdparty imports
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Projects imports
from .views import ShopUserViewSet, me

router = DefaultRouter()
router.register(
    r'users',
    ShopUserViewSet,
    basename='users_v1'
)

urlpatterns = [
    path('users/me', me, name='users_me'),
    path('', include(router.urls)),
]
