from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from store import models, serializers
from django.shortcuts import get_object_or_404
from django.db.models import Count


@api_view()
def hi_rest_framework(request):
    """Just a simple api response by DRF"""
    return Response("hello from DRF", status.HTTP_202_ACCEPTED)


@api_view()
def hi_rest_framework_detail(request, id):
    """Detail api view for hi/ endpoint"""
    return Response(f"your given ID is: {id}", status.HTTP_200_OK)


@api_view()
def get_product_list(request):
    """Get all of Products in database"""
    product = models.Product.objects.select_related("collection").all()
    serializer = serializers.ProductSimpleSerializer(
        product,
        many=True,
        context={"request": request},
    )
    return Response(serializer.data)


@api_view()
def get_product_details(request, id):
    """Get some of our Products details"""
    try:
        product = models.Product.objects.get(pk=id)
        serializer = serializers.ProductSimpleSerializer(
            product,
            context={"request": request},
        )
        return Response(serializer.data)

    except models.Product.DoesNotExist:
        return Response(
            f"we do not have a product with ID: {id}",
            status.HTTP_404_NOT_FOUND,
        )


@api_view()
def get_product_details_optimized(request, id):
    """Get some of our Products details optimized"""
    product = get_object_or_404(models.Product, pk=id)
    serializer = serializers.ProductSimpleSerializer(product)
    return Response(serializer.data)


@api_view()
def get_collection_detail(request, pk):
    collection = get_object_or_404(models.Collection, pk=pk)
    serializer = serializers.CollectionSimpleSerializer(collection)
    return Response(serializer.data)


@api_view(["GET", "POST"])
def product_list(request):
    if request.method == "GET":
        product = models.Product.objects.select_related("collection").all()
        serializer = serializers.ProductSerializer(product, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = serializers.ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def product_detail(request, pk):
    product = get_object_or_404(models.Product, pk=pk)

    if request.method == "GET":
        serializer = serializers.ProductSerializer(product)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = serializers.ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    elif request.method == "DELETE":
        if product.order_item_set.count() > 0:
            return Response(
                f"Can Not delete the {product.title} in a OrderItem",
                status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        product.delete()
        return Response(
            f"Product {product.title} Deleted successfully",
            status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET", "POST"])
def collection_list(request):
    if request.method == "GET":
        collection = models.Collection.objects.annotate(
            product_count=Count("product")
        ).all()
        serializer = serializers.CollectionSerializer(collection, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = serializers.CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def collection_detail(request, pk):
    collection = get_object_or_404(
        models.Collection.objects.annotate(product_count=Count("product")), pk=pk
    )

    if request.method == "GET":
        serializer = serializers.CollectionSerializer(collection)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = serializers.CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    elif request.method == "DELETE":
        if collection.product_set.count() > 0:
            return Response(
                f"Collection {collection.title} still contains products!",
                status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        collection.delete()
        return Response(
            f"Collection {collection.title} successfully deleted",
            status.HTTP_204_NO_CONTENT,
        )
