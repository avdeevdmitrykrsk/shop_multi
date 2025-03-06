# Standart lib imports
from dataclasses import dataclass

# Thirdparty imports
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import (
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.viewsets import ModelViewSet

# Projects imports
from .crud_for_rating_shopping_cart import (
    create_rating_favorite_shopping_cart,
    delete_rating_favorite_shopping_cart,
)
from products.constants import (
    FAVORITE_ALREADY_EXIST,
    RATING_ALREADY_EXIST,
    SHOPPING_CART_ALREADY_EXIST,
)
from products.exceptions import ProductAlreadyExist
from products.models import Favorite, Product, Rating, ShoppingCart
from products.serializers import (
    FavoriteSerializer,
    GetProductSerializer,
    ProductSerializer,
    RatingSerializer,
    ShoppingCartSerializer,
)
from users.permissions import IsSuperuserOrReadOnly

SAFE_ACTIONS = ('list', 'retrieve')


@permission_classes((IsAuthenticatedOrReadOnly,))
class RatingFavoriteShoppingCartViewSet(ModelViewSet):

    SERIALIZER_MAPPING = {
        'rating': RatingSerializer,
        'favorite': FavoriteSerializer,
        'shopping_cart': ShoppingCartSerializer,
    }
    QUERYSET_MAPPING = {
        'rating': Rating.objects.all(),
        'favorite': Favorite.objects.all(),
        'shopping_cart': ShoppingCart.objects.all(),
    }

    def get_path_segment(self):
        return self.request.path.strip('/').split('/')[-1]

    def get_serializer_class(self):
        path_segment = self.get_path_segment()
        return self.SERIALIZER_MAPPING.get(path_segment)

    def get_queryset(self):
        path_segment = self.get_path_segment()
        return self.QUERYSET_MAPPING.get(path_segment)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        extra_data = None

        if 'rating' in self.get_path_segment():
            extra_data = {
                'score': request.data.get('score'),
            }

        return create_rating_favorite_shopping_cart(
            request,
            self.get_serializer_class(),
            pk=kwargs.get('pk'),
            extra_data=extra_data,
        )

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        return delete_rating_favorite_shopping_cart(
            request,
            self.get_queryset(),
            pk=kwargs.get('pk'),
        )


@permission_classes((IsAuthenticatedOrReadOnly, IsSuperuserOrReadOnly))
class ProductViewSet(ModelViewSet):

    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        return Product.objects.get_annotated_queryset(self.request.user)

    def get_serializer_class(self):
        if self.action in SAFE_ACTIONS:
            return GetProductSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
