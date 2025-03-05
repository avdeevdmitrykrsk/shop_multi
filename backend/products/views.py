# Standart lib imports
from dataclasses import dataclass

# Thirdparty imports
from django.db import transaction
from django.shortcuts import get_object_or_404
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

from products.constants import (
    FAVORITE_ALREADY_EXIST,
    RATING_ALREADY_EXIST,
    SHOPPING_CART_ALREADY_EXIST,
)

# Projects imports
from .crud_for_rating_shopping_cart import (  # delete_rating_favorite_shopping_cart,
    create_rating_favorite_shopping_cart,
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

    def get_serializer_class(self):
        path = self.request.path

        if 'rating' in path:
            serializer = RatingSerializer
        elif 'favorite' in path:
            serializer = FavoriteSerializer
        elif 'shopping_cart' in path:
            serializer = ShoppingCartSerializer
        return serializer

    def get_queryset(self):
        path = self.request.path

        if 'rating' in path:
            queryset = Rating.objects.all()
        elif 'favorite' in path:
            queryset = Favorite.objects.all()
        elif 'shopping_cart' in path:
            queryset = ShoppingCart.objects.all()
        return queryset

    def get_err_message(self, request):
        err_messages = {
            'rating': RATING_ALREADY_EXIST,
            'favorite': FAVORITE_ALREADY_EXIST,
            'shopping_cart': SHOPPING_CART_ALREADY_EXIST,
        }
        return err_messages[request.path.split('/')[-2]]

    def _has_already_exist(self, request, *args, **kwargs):

        if (
            self.get_queryset()
            .filter(
                user=request.user,
                product=Product.objects.get(id=kwargs.get('pk')),
            )
            .exists()
        ):
            return True

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        if self._has_already_exist(request, *args, **kwargs):
            raise ProductAlreadyExist(self.get_err_message(request))

        return create_rating_favorite_shopping_cart(
            request,
            self.get_serializer_class(),
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
