from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Inventory
from .serializers import (
    InventoryReadSerializer,
    InventoryWriteSerializer,
)


class InventoryViewSet(ModelViewSet):
    queryset = Inventory.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return InventoryReadSerializer

        return InventoryWriteSerializer

    def get_queryset(self):
        return Inventory.objects.select_related("product")

    @action(detail=False, methods=["post"])
    def bulk_create(self, request):

        serializer = self.get_serializer(data=request.data, many=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
