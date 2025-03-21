# Thirdparty imports
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Projects imports
from .views import (
    CategoryViewSet,
    OrderViewSet,
    ProductViewSet,
    RatingFavoriteShoppingCartViewSet,
    SubCategoryViewSet,
)

router = DefaultRouter()
router.register(
    r'shopping_cart',
    RatingFavoriteShoppingCartViewSet,
    basename='shopping_cart_v1',
)
router.register(r'orders', OrderViewSet, basename='orders_v1')
router.register(r'products', ProductViewSet, basename='products_v1')
router.register(r'category', CategoryViewSet, basename='category_v1')
router.register(
    r'sub_category', SubCategoryViewSet, basename='sub_category_v1'
)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'products/<int:pk>/rating/',
        RatingFavoriteShoppingCartViewSet.as_view(
            {'post': 'create', 'get': 'retrieve'}
        ),
        name='rating_favorite_shopping_cart',
    ),
    path(
        'products/<int:pk>/favorite/',
        RatingFavoriteShoppingCartViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        ),
        name='favorite',
    ),
    path(
        'products/<int:pk>/shopping_cart/',
        RatingFavoriteShoppingCartViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        ),
        name='shopping_cart',
    ),
]
