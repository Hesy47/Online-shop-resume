from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from store import models, serializers
from django.shortcuts import get_object_or_404
from django.db.models import Count


class ProductList(APIView):
    def get(self, request):
        queryset = models.Product.objects.select_related("collection").all()
        serializer = serializers.ProductSerializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request):
        serializer = serializers.ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class ProductDetail(APIView):
    def get(self, request, pk):
        queryset = get_object_or_404(models.Product, pk=pk)
        serializer = serializers.ProductSerializer(queryset)
        return Response(serializer.data, status.HTTP_200_OK)

    def put(self, request, pk):
        queryset = get_object_or_404(models.Product, pk=pk)
        serializer = serializers.ProductSerializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

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


class CollectionList(APIView):
    def get(self, request):
        queryset = models.Collection.objects.annotate(
            product_count=Count("product")
        ).all()
        serializer = serializers.CollectionSerializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request):
        serializer = serializers.CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


class CollectionDetail(APIView):
    def get(self, request, pk):
        queryset = get_object_or_404(
            models.Collection.objects.annotate(product_count=Count("product")), pk=pk
        )
        serializer = serializers.CollectionSerializer(queryset)
        return Response(serializer.data, status.HTTP_200_OK)

    def put(self, request, pk):
        queryset = get_object_or_404(models.Collection, pk=pk)
        serializer = serializers.CollectionSerializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

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
