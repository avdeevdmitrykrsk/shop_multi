# Thirdparty imports
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Avg, F
from rest_framework import serializers

# Projects imports
from .constants import DEFAULT_RATING, MIN_PRODUCT_PRICE, PRICE_ERR_MSG
from products.models import (
    Favorite,
    Product,
    ProductProperty,
    Property,
    Rating,
    ShoppingCart,
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


class FavoriteSerializer(BaseRatingFavoriteShoppingCartSerializer):

    class Meta(BaseRatingFavoriteShoppingCartSerializer.Meta):
        model = Favorite

    def create(self, validated_data):
        instance = validated_data.get('product')
        setattr(instance, 'is_in_favorite', True)
        instance.save()
        return super().create(validated_data)


class ShoppingCartSerializer(BaseRatingFavoriteShoppingCartSerializer):

    class Meta(BaseRatingFavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart

    def create(self, validated_data):
        instance = validated_data.get('product')
        setattr(instance, 'is_in_shopping_cart', True)
        instance.save()
        return super().create(validated_data)


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


class GetProductSerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()
    creator = ShopUserRetrieveSerializer()
    rating = serializers.SerializerMethodField(method_name='get_rating')

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
        fields = ('name', 'description', 'price', 'properties')
        read_only_fields = ('creator',)

    def validate_price(self, value):
        if value < MIN_PRODUCT_PRICE:
            raise serializers.ValidationError(PRICE_ERR_MSG)
        return value

    def to_representation(self, instance):
        serializer = GetProductSerializer(instance)
        return serializer.data

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
        instance = Product.objects.create(**validated_data)

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
