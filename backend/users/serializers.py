from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, ValidationError

User = get_user_model()


class ShopUserCreateSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone_number',
        )


class ShopUserRetrieveSerializer(ModelSerializer):

    class Meta(ShopUserCreateSerializer.Meta):
        pass
