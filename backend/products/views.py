# Thirdparty imports
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.viewsets import ModelViewSet

# Projects imports
from .crud_for_rating_shopping_cart import (  # delete_rating_favorite_shopping_cart,
    create_rating_favorite_shopping_cart,
)
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


class FavoriteViewSet(ModelViewSet):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Favorite.objects.all()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return create_rating_favorite_shopping_cart(
            request,
            FavoriteSerializer,
            pk=kwargs.get('pk'),
        )

    # def destroy(self, request, *args, **kwargs):
    #     return delete_rating_favorite_shopping_cart(
    #         request, ShoppingCart, kwargs.get('pk')
    #     )


class ShoppingCartViewSet(ModelViewSet):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = ShoppingCart.objects.all()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return create_rating_favorite_shopping_cart(
            request,
            ShoppingCartSerializer,
            pk=kwargs.get('pk'),
        )


class RatingViewSet(ModelViewSet):

    queryset = Rating.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return create_rating_favorite_shopping_cart(
            request,
            pk=kwargs.get('pk'),
            extra_data={
                'score': request.data.get('score'),
            },
        )


class ProductViewSet(ModelViewSet):

    http_method_names = ('get', 'post', 'patch', 'delete')
    queryset = Product.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsSuperuserOrReadOnly)

    def get_serializer_class(self):
        if self.action in SAFE_ACTIONS:
            return GetProductSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
