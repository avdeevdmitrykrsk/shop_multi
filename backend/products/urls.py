# Thirdparty imports
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Projects imports
from .views import (
    FavoriteViewSet,
    ProductViewSet,
    RatingViewSet,
    ShoppingCartViewSet,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products_v1')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'products/<int:pk>/rating/',
        RatingViewSet.as_view({'post': 'create', 'get': 'retrieve'}),
        name='rating',
    ),
    path(
        'products/<int:pk>/favorite/',
        FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='favorite',
    ),
    path(
        'products/<int:pk>/shopping_cart/',
        ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='shopping_cart',
    ),
]
