from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.mixins import DestroyModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework import permissions
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from store import models, serializers, filters, pagination
from store.permissions import IsAdminOrReadOnly


class ProductViewSet(ModelViewSet):
    queryset = models.Product.objects.select_related("collection").all()
    serializer_class = serializers.ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = pagination.ProductPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = filters.ProductFilter
    search_fields = ["title"]
    ordering_fields = ["price"]

    def destroy(self, request, *args, **kwargs):
        if models.OrderItem.objects.filter(product_id=kwargs["pk"]).count() > 0:
            return Response(
                f"This Product is still in OrderItems",
                status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = models.Collection.objects.annotate(product_count=Count("product")).all()
    serializer_class = serializers.CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = pagination.CollectionPagination

    def destroy(self, request, *args, **kwargs):
        if models.Product.objects.filter(collection_id=kwargs["pk"]).count() > 0:
            return Response(
                "This Collection still contains products",
                status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = serializers.ReviewSerializer

    def get_queryset(self):
        return models.Review.objects.filter(
            product_id=self.kwargs["product_pk"]
        ).select_related("product")

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}


class CartViewSet(
    CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = models.Cart.objects.prefetch_related("items__product").all()
    serializer_class = serializers.CartSerializer


class CartItemViewSet(ModelViewSet):

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.AddCartItemSerializer

        elif self.request.method == "PUT":
            return serializers.UpdateCartItemSerializer

        return serializers.CartItemSerializer

    def get_queryset(self):
        return models.CartItem.objects.filter(
            cart_id=self.kwargs["cart_pk"]
        ).select_related("product")

    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}


class CustomerViewSet(ModelViewSet):
    serializer_class = serializers.CustomerSerializer
    queryset = models.Customer.objects.all()
    permission_classes = [permissions.IsAdminUser]

    @action(
        detail=False,
        methods=["GET", "PUT"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def me(self, request):
        customer = models.Customer.objects.get(user_id=request.user.id)

        if request.method == "GET":
            serializer = serializers.CustomerSerializer(customer)
            return Response(serializer.data)

        elif request.method == "PUT":
            serializer = serializers.CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = serializers.CreateOrderSerializer(
            data=request.data, context={"user_id": self.request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = serializers.OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.CreateOrderSerializer

        elif self.request.method == "PUT":
            return serializers.UpdateOrderSerializer

        return serializers.OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return models.Order.objects.prefetch_related("items")

        customer = models.Customer.objects.only("id").get(user_id=user.id)
        return models.Order.objects.filter(customer_id=customer)


class ProductImageViewSet(ModelViewSet):
    serializer_class = serializers.ProductImageSerializer

    def get_queryset(self):
        return models.ProductImage.objects.filter(
            product_id=self.kwargs["product_pk"]
        ).select_related("product")

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}
