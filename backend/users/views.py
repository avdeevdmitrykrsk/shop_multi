# Thirdparty imports
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from djoser.views import UserViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

# Projects imports
from .permissions import AllBlock
from .serializers import ShopUserCreateSerializer, ShopUserRetrieveSerializer

User = get_user_model()


class ShopUserViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = ShopUserCreateSerializer
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        return (
            ShopUserCreateSerializer
            if (self.request.method == 'POST')
            else ShopUserRetrieveSerializer
        )


@api_view(['get', 'patch', 'delete'])
@permission_classes([IsAuthenticated])
def me(request, *args, **kwargs):
    serializer = ShopUserRetrieveSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
