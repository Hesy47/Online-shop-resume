from django.db import transaction
from rest_framework import serializers
from store import models
from decimal import Decimal
from store.signals import order_created


class CollectionSerializer(serializers.ModelSerializer):
    """Main ModelSerializer for our Collection class"""

    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Collection
        fields = ["id", "title", "product_count"]


class ProductImageSerializer(serializers.ModelSerializer):

    product = serializers.CharField(read_only=True)

    class Meta:
        model = models.ProductImage
        fields = ["id", "product", "image"]

    def create(self, validated_data):
        product_id = self.context["product_id"]
        return models.ProductImage.objects.create(
            product_id=product_id, **validated_data
        )


class ProductSerializer(serializers.ModelSerializer):
    """Main ModelSerializer for our Product class"""

    collection_name = serializers.StringRelatedField(source="collection")
    price_after_tax = serializers.SerializerMethodField(method_name="calculate_tax")
    images = ProductImageSerializer(many=True)

    class Meta:
        model = models.Product
        fields = [
            "id",
            "title",
            "price",
            "price_after_tax",
            "inventory",
            "collection",
            "collection_name",
            "description",
            "images",
        ]

    def calculate_tax(self, pro):
        return pro.price * Decimal(1.2)


class ReviewSerializer(serializers.ModelSerializer):
    """Main ModelSerializer for our Review class"""

    product_name = serializers.CharField(read_only=True, source="product")

    class Meta:
        model = models.Review
        fields = ["id", "name", "date", "product", "product_name", "description"]
        extra_kwargs = {"product": {"read_only": True}}

    def create(self, validated_data):
        product_id = self.context["product_id"]
        return models.Review.objects.create(product_id=product_id, **validated_data)


class ProductCartItemSerializer(serializers.ModelSerializer):
    """Our assistant product modelSerializer for CartItemSerializer"""

    class Meta:
        model = models.Product
        fields = ["id", "title", "price"]


class CartItemSerializer(serializers.ModelSerializer):
    """Main ModelSerializer for our CartItem class"""

    product = ProductCartItemSerializer()
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    class Meta:
        model = models.CartItem
        fields = ["id", "quantity", "product", "total_price"]

    def get_total_price(self, cart_item):
        return cart_item.product.price * cart_item.quantity

    def create(self, validated_data):
        return super().create(validated_data)


class AddCartItemSerializer(serializers.ModelSerializer):

    product_id = serializers.IntegerField()

    class Meta:
        model = models.CartItem
        fields = ["id", "product_id", "quantity"]

    def validate_product_id(self, value):
        if not models.Product.objects.filter(pk=value):
            raise serializers.ValidationError(f"We Do Not have {value} as a product id")
        return value

    def save(self, **kwargs):
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]
        cart_id = self.context["cart_id"]

        try:
            cart_item = models.CartItem.objects.get(
                product_id=product_id, cart_id=cart_id
            )
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item

        except models.CartItem.DoesNotExist:
            self.instance = models.CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )

        return self.instance


class UpdateCartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CartItem
        fields = ["quantity"]


class CartSerializer(serializers.ModelSerializer):
    """Main ModelSerializer for our Cart class"""

    items = CartItemSerializer(many=True, read_only=True)
    total_price_payment = serializers.SerializerMethodField(
        method_name="get_total_price"
    )

    class Meta:
        model = models.Cart
        fields = ["id", "created_at", "items", "total_price_payment"]
        extra_kwargs = {
            "created_at": {"read_only": True},
            "id": {"read_only": True},
        }

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.price for item in cart.items.all()])


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Customer
        fields = [
            "id",
            "phone",
            "birth_date",
            "membership",
            "user_id",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductCartItemSerializer()

    class Meta:
        model = models.OrderItem
        fields = [
            "id",
            "quantity",
            "unit_price",
            "product",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = models.Order
        fields = ["id", "placed_at", "payment_status", "customer", "items"]


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not models.Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("This shopping cart id is not Valid!")

        if models.CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError("You do not have any item in you cart!")

        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():

            cart_id = self.validated_data["cart_id"]

            customer_id = models.Customer.objects.get(user_id=self.context["user_id"])
            order = models.Order.objects.create(customer=customer_id)
            cart_items = models.CartItem.objects.select_related("product").filter(
                cart_id=cart_id
            )

            order_items = [
                models.OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.price,
                    quantity=item.quantity,
                )
                for item in cart_items
            ]

            models.OrderItem.objects.bulk_create(order_items)
            models.Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(sender=self.__class__, order=order)
            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ["payment_status"]


# class ProductImageSerializer(serializers.ModelSerializer):

#     product = serializers.CharField(read_only=True)

#     class Meta:
#         model = models.ProductImage
#         fields = ["id", "product", "image"]

#     def create(self, validated_data):
#         product_id = self.context["product_id"]
#         return models.ProductImage.objects.create(
#             product_id=product_id, **validated_data
#         )
