# Thirdparty imports
from django.urls import path
from rest_framework.routers import DefaultRouter

# Projects imports
from .views import ProductViewSet

router = DefaultRouter()
router.register(
    r'v1/products/create',
    ProductViewSet,
    basename='products_list_v1'
)

urlpatterns = router.urls
