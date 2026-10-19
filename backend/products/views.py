import json
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from config.redis_client import redis_client
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import ProductReadSerializer, ProductWriteSerializer

from .pagination import ProductsPagination

class ProductViewSet(ModelViewSet):
    # parser_classes = [MultiPartParser,FormParser]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    permission_classes = [IsAuthenticated]
    search_fields = ["name", "description", "sku"]
    filterset_fields = ["is_featured", "category"]
    ordering_fields = ["created_at", "price"]
    pagination_class = ProductsPagination

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ProductReadSerializer
        return ProductWriteSerializer

    def get_queryset(self):
        queryset = (
            Product.objects.filter(
                is_deleted=False, is_active=True, tenant=self.request.user.tenant
            )
            .select_related("category")
            .prefetch_related("tags",'images')
            .order_by('-created_at')
        )

        min_price = self.request.query_params.get("min_price")
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except (ValueError, TypeError):
                pass

        max_price = self.request.query_params.get("max_price")
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except (ValueError, TypeError):
                pass

        color = self.request.query_params.get("color")
        if color:
            queryset = queryset.filter(specifications__contains={"color": color.lower()})

        size = self.request.query_params.get("size")
        if size:
            queryset = queryset.filter(specifications__sizes__contains=[size])

        key = self.request.query_params.get("spec_key")
        value = self.request.query_params.get("spec_value")
        if key and value:
            queryset = queryset.filter(specifications__contains={key: value})

        return queryset

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)

    def _clear_cache(self, tenant_id):
        try:
            for key in redis_client.scan_iter(match=f"products:{tenant_id}*"):
                redis_client.delete(key)
        except Exception:
            pass

    def list(self, request, *args, **kwargs):
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 20)
        search = request.query_params.get("search", "")
        ordering = request.query_params.get("ordering", "-created_at")
        category = request.query_params.get("category", "")
        is_featured = request.query_params.get("is_featured", "")
        min_price = request.query_params.get("min_price", "")
        max_price = request.query_params.get("max_price", "")
        color = request.query_params.get("color", "")
        size = request.query_params.get("size", "")

        cache_key = (
            f"products:{request.user.tenant.id}:"
            f"page:{page}:"
            f"page_size:{page_size}:"
            f"search:{search}:"
            f"ordering:{ordering}:"
            f"category:{category}:"
            f"is_featured:{is_featured}:"
            f"min_price:{min_price}:"
            f"max_price:{max_price}:"
            f"color:{color}:"
            f"size:{size}"
        )

        try:
            cached = redis_client.get(cache_key)
            if cached:
                return Response(json.loads(cached))
        except Exception:
            pass

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)

            try:
                redis_client.set(cache_key, json.dumps(response.data), ex=300)
            except Exception:
                pass

            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):

        product = self.get_object()

        product.is_deleted = True

        product.save()

        self._clear_cache(request.user.tenant.id)

        return Response(status=204)

    @action(detail=False, methods=["post"])
    def bulk_create(self, request):

        self._clear_cache(request.user.tenant.id)

        serializer = self.get_serializer(
            data=request.data,
            many=True
        )

        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save()

        return Response(
            serializer.data,
            status=201
        )

    def create(self, request, *args, **kwargs):
        self._clear_cache(request.user.tenant.id)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._clear_cache(request.user.tenant.id)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._clear_cache(request.user.tenant.id)
        return super().partial_update(request, *args, **kwargs)



