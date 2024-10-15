from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from store import models, serializers
from django.shortcuts import get_object_or_404
from django.db.models import Count


class ProductList(ListCreateAPIView):
    """Products-List GenericView with overwriting(Not Necessary Here!)"""

    def get_queryset(self):
        return models.Product.objects.select_related("collection").all()

    def get_serializer_class(self):
        return serializers.ProductSerializer


class ProductDetail(RetrieveUpdateDestroyAPIView):
    """Product-Detail GenericView with default"""

    queryset = models.Product.objects.select_related("collection").all()
    serializer_class = serializers.ProductSerializer

    def delete(self, request, pk):
        queryset = get_object_or_404(models.Product, pk=pk)

        if queryset.order_item_set.count() > 0:
            return Response(
                f"Product {queryset.title} still is in OrderItems",
                status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        queryset.delete()
        return Response(
            f"Product {queryset.title} successfully deleted",
            status.HTTP_204_NO_CONTENT,
        )


class CollectionList(ListCreateAPIView):
    """Collections-List GenericView with default"""

    queryset = models.Collection.objects.annotate(product_count=Count("product")).all()
    serializer_class = serializers.CollectionSerializer


class CollectionDetail(RetrieveUpdateDestroyAPIView):
    """Collection-Detail GenericView with overwriting(Not Necessary Here!)"""

    def get_queryset(self):
        return models.Collection.objects.annotate(product_count=Count("product")).all()

    def get_serializer_class(self):
        return serializers.CollectionSerializer

    def delete(self, request, pk):
        queryset = get_object_or_404(models.Collection, pk=pk)

        if queryset.product_set.count() > 0:
            return Response(
                f"Collection {queryset.title} still is contain products",
                status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        queryset.delete()
        return Response(
            f"Collection {queryset.title} successfully deleted",
            status.HTTP_204_NO_CONTENT,
        )
