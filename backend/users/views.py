from django.contrib.auth import get_user_model
from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet

from .serializers import ShopUserCreateSerializer

User = get_user_model()


class ShopUserViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = ShopUserCreateSerializer

    def perform_create(self, *args, **kwargs):
        super().create
        print({'args': args})
        print({'kwargs': kwargs})
