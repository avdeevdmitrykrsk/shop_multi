# Thirdparty imports
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db import models

# Projects imports
from .models import ShopUser

User = get_user_model()


class ShopUserAuthenticationBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = ShopUser.objects.get(
                models.Q(email=email) | models.Q(phone_number=email)
            )
        except ShopUser.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
