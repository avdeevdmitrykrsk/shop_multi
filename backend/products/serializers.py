# Thirdparty imports
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Avg, F
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

# Projects imports
from .constants import DEFAULT_RATING, MIN_PRICE_VALUE, PRICE_ERR_MSG
from products.models import (
    Category,
    Favorite,
    Product,
    ProductProperty,
    ProductSubCategory,
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


class PropertyValueSerializer(BaseRatingFavoriteShoppingCartSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all())

    class Meta:
        model = ProductProperty
        fields = ('id', 'value')


class GetProductPropertySerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='property_id')
    name = serializers.SerializerMethodField(method_name='get_name')

    class Meta:
        model = ProductProperty
        fields = ('id', 'name', 'value')

    def get_name(self, obj):
        return Property.objects.get(id=obj.property.id).name


class GetProductSubCategorySerializer(serializers.ModelSerializer):
    sub_category = SubCategorySerializer()

    class Meta:
        model = ProductSubCategory
        fields = ('id', 'sub_category')


class GetProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    sub_categories = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()
    creator = ShopUserRetrieveSerializer(read_only=True)
    rating = serializers.SerializerMethodField(method_name='get_rating')
    is_favorited = serializers.BooleanField(default=False, read_only=True)
    is_in_shopping_cart = serializers.BooleanField(
        default=False, read_only=True
    )

    class Meta:
        model = Product
        fields = '__all__'

    def get_rating(self, instance):
        rating = Rating.objects.filter(product_id=instance.id).aggregate(
            rating=Avg('score')
        )['rating']

        if not rating:
            rating = DEFAULT_RATING

        return rating

    def get_sub_categories(self, instance):
        sub_categories = (
            instance.sub_categories.all()
        )
        serializer = SubCategorySerializer(
            sub_categories, many=True
        )
        return serializer.data

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
        fields = ('name', 'description', 'price', 'category', 'properties')
        read_only_fields = ('creator',)

    def validate_price(self, value):
        if value < MIN_PRICE_VALUE:
            raise serializers.ValidationError(PRICE_ERR_MSG)
        return value

    def to_representation(self, instance):
        serializer = GetProductSerializer(instance)
        return serializer.data

    def sub_categories_create(self, sub_categories, product):
        for sub_category in sub_categories:
            ProductSubCategory.objects.create(
                product=product, sub_category=sub_category
            )

    def product_properties_create(self, properties, product):
        for property in properties:
            ProductProperty.objects.create(
                product=product,
                property=property.get('id'),
                value=property.get('value'),
            )

    @transaction.atomic
    def create(self, validated_data):
        properties_data = validated_data.pop('properties')
        sub_categories_data = validated_data.pop('sub_categories')
        instance = Product.objects.create(**validated_data)

        self.sub_categories_create(sub_categories_data, instance)
        self.product_properties_create(properties_data, instance)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        properties = validated_data.pop('properties')

        if properties:
            for property in properties:
                instances = ProductProperty.objects.filter(
                    product_id=instance.id
                )
                instances.delete()

                self.product_properties_create(properties, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
