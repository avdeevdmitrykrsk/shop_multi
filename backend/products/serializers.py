# Standart lib imports
from collections import OrderedDict

# Thirdparty imports
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Avg, F, Max, Prefetch
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

# Projects imports
from products.constants import (
    DEFAULT_ARTICLE_DIGIT,
    DEFAULT_RATING,
    MIN_PRICE_VALUE,
    PRICE_ERR_MSG,
)
from products.models import (
    Article,
    Category,
    Favorite,
    Product,
    ProductProperty,
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
        fields = ('user', 'product')


class RatingSerializer(BaseRatingFavoriteShoppingCartSerializer):

    class Meta(BaseRatingFavoriteShoppingCartSerializer.Meta):
        model = Rating
        fields = ('user', 'product', 'score')
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
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(), fields=('user', 'product')
            )
        ]


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


class GetProductSerializer(serializers.ModelSerializer):
    article = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    sub_category = SubCategorySerializer(read_only=True)
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
            'properties',
            'price',
            'rating',
            'article',
            'creator',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_article(self, instance):
        print(instance.article_by_product)
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
        )
        read_only_fields = (
            'article',
            'creator',
            'created_at',
            'updated_at',
            'article',
        )

    def validate_price(self, value):
        if value < MIN_PRICE_VALUE:
            raise serializers.ValidationError(PRICE_ERR_MSG)
        return value

    def to_representation(self, instance):
        serializer = GetProductSerializer(instance)
        return serializer.data

    def _get_prefix(self, instance):
        return (
            f'{instance.category.name[:3].upper()}-'
            f'{instance.sub_category.name[:3].upper()}'
        )

    def _get_unique_digit(self):
        max_digit = (
            Article.objects.all()
            .values('article')
            .aggregate(Max('article'))['article__max']
        )

        if max_digit is not None:
            max_digit = int(max_digit.split(':')[-1])
            max_digit += 1
            return str(max_digit)

        return DEFAULT_ARTICLE_DIGIT

    def article_create(self, instance):
        prefix = self._get_prefix(instance)
        unique_digit = self._get_unique_digit()
        article = f'{prefix}:{unique_digit}'

        Article.objects.create(product=instance, article=article)

    def product_properties_create(self, properties, product):
        for property in properties:
            ProductProperty.objects.create(product=product, **property)

    @transaction.atomic
    def create(self, validated_data):
        properties_data = validated_data.pop('properties')
        instance = Product.objects.create(**validated_data)

        self.article_create(instance)
        self.product_properties_create(properties_data, instance)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        properties = validated_data.pop('properties')

        if properties is not None:
            instance.product_property.clear()
            self.product_properties_create(properties, instance)

        return super().update(instance, validated_data)
