# Thirdparty imports
from rest_framework.decorators import permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.viewsets import ModelViewSet

# Projects imports
from make_pc.models import PcDIY
from make_pc.serializers import GetPcDIYSerializer, PcDIYSerializer
from products.models import Product
from products.views import SAFE_ACTIONS


@permission_classes((AllowAny,))
class MakePcViewSet(ModelViewSet):
    queryset = PcDIY.objects.all()

    def get_serializer_class(self):
        if self.request.method in SAFE_ACTIONS:
            return GetPcDIYSerializer
        return PcDIYSerializer
