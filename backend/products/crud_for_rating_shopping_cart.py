# Thirdparty imports
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

# Projects imports
from products.exceptions import ProductAlreadyExist
from products.models import Product, Rating
from products.serializers import GetProductSerializer, RatingSerializer


def create_rating_favorite_shopping_cart(
    request, serializer_class, pk, extra_data=None
):
    instance = get_object_or_404(Product, id=pk)

    data = {'user': request.user.id, 'product': instance.id}
    if extra_data:
        data.update(extra_data)

    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    instance = get_object_or_404(
        Product.objects.get_annotated_queryset(request.user), id=pk
    )

    serializer = GetProductSerializer(instance)
    return Response(data=serializer.data, status=status.HTTP_201_CREATED)


def delete_rating_favorite_shopping_cart(request, queryset, pk):
    get_object_or_404(Product, id=pk)

    instance = queryset.filter(user=request.user, product_id=pk)
    count, _ = instance.delete()

    if not count:
        raise ValidationError(
            'Продукт отсутствует в списке '
            f'\'{instance.model._meta.verbose_name}\'.'
        )

    return Response(status=status.HTTP_204_NO_CONTENT)
