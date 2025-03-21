# Standart lib imports
from collections import OrderedDict

# Thirdparty imports
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Avg, F, Max, Prefetch
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

# Projects imports
from products.article import article_util
from products.constants import (
    DEFAULT_RATING,
    MAX_NAME_LENGTH,
    MIN_NAME_LENGTH,
    MIN_PRICE_VALUE,
    PRICE_ERR_MSG,
    PRODUCT_NAME_ERR_MSG,
)
from products.models import (
    Article,
    Category,
    Favorite,
    Order,
    OrderProduct,
    Product,
    ProductProperty,
    ProductType,
    Property,
    Rating,
    ShoppingCart,
    SubCategory,
)
from users.serializers import ShopUserRetrieveSerializer

User = get_user_model()


class BaseRatingFavoriteShoppingCartSerializer(serializers.ModelSerializer):
    """Абстрактный сериализатор для Rating/Favorite/ShoppingCart"""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )

    class Meta:
        fields = ('id', 'user', 'product')
        read_only_fields = ('user',)


class RatingSerializer(BaseRatingFavoriteShoppingCartSerializer):

    class Meta(BaseRatingFavoriteShoppingCartSerializer.Meta):
        model = Rating
        fields = ('id', 'user', 'product', 'score')
        validators = [
            UniqueTogetherValidator(
                queryset=Rating.objects.all(), fields=('user', 'product')
            )
        ]


class FavoriteSerializer(BaseRatingFavoriteShoppingCartSerializer):

    class Meta(BaseRatingFavoriteShoppingCartSerializer.Meta):
        model = Favorite
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(), fields=('user', 'product')
            )
        ]


class ShoppingCartSerializer(BaseRatingFavoriteShoppingCartSerializer):

    class Meta(BaseRatingFavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SubCategory
        fields = '__all__'


class PropertyValueSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='property_id')
    value = serializers.CharField()

    class Meta:
        model = ProductProperty
        fields = ('id', 'value')


class GetProductPropertySerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='property_id')
    name = serializers.SerializerMethodField()

    class Meta:
        model = ProductProperty
        fields = ('id', 'name', 'value')

    def get_name(self, instance):
        return instance.property.name


class ProductTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductType
        fields = ('id', 'name')


class GetProductSerializer(serializers.ModelSerializer):
    article = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    sub_category = SubCategorySerializer(read_only=True)
    product_type = ProductTypeSerializer(read_only=True)
    properties = serializers.SerializerMethodField()
    creator = ShopUserRetrieveSerializer(read_only=True)
    rating = serializers.IntegerField(default=DEFAULT_RATING)
    is_favorited = serializers.BooleanField(default=False, read_only=True)
    is_in_shopping_cart = serializers.BooleanField(
        default=False, read_only=True
    )

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'category',
            'sub_category',
            'product_type',
            'properties',
            'price',
            'rating',
            'article',
            'creator',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_article(self, instance):
        return instance.article_by_product.article

    def get_properties(self, instance):
        product_properties = instance.product_property_prod.all()
        serializer = GetProductPropertySerializer(
            product_properties, many=True
        )
        return serializer.data


class ProductSerializer(serializers.ModelSerializer):

    properties = PropertyValueSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            'name',
            'description',
            'price',
            'category',
            'sub_category',
            'properties',
            'product_type',
        )
        read_only_fields = (
            'article',
            'creator',
            'created_at',
            'updated_at',
        )

    def to_representation(self, instance):
        return GetProductSerializer(instance).data

    def product_properties_create(self, properties, product):
        data = []
        for property in properties:
            data.append(ProductProperty(product=product, **property))
        ProductProperty.objects.bulk_create(data)

    @transaction.atomic
    def create(self, validated_data):
        properties_data = validated_data.pop('properties')

        instance = Product.objects.create(**validated_data)
        article_util.create(instance)
        self.product_properties_create(properties_data, instance)

        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        if validated_data.get('properties'):
            properties = validated_data.pop('properties')
            instance.product_property.clear()
            self.product_properties_create(properties, instance)

        return super().update(instance, validated_data)


class GetOrderSerializer(serializers.ModelSerializer):

    products = GetProductSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):

    products = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), many=True
    )

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('customer',)

    def to_representation(self, instance):
        return GetOrderSerializer(instance).data

    def order_products_create(self, products, order):
        data = []
        for product in products:
            data.append(OrderProduct(order=order, product=product))
        OrderProduct.objects.bulk_create(data)

    def _calculate_total_price(self, products):
        return sum(
            [Product.objects.get(id=product.id).price for product in products]
        )

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        total_price = self._calculate_total_price(products_data)

        instance = Order.objects.create(
            **validated_data, total_price=total_price
        )
        self.order_products_create(products_data, instance)
        return instance
