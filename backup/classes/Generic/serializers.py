from rest_framework import serializers
from store import models
from decimal import Decimal


class CollectionSerializer(serializers.ModelSerializer):
    """Main ModelSerializer for our Collection class"""

    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Collection
        fields = ["id", "title", "product_count"]


class ProductSerializer(serializers.ModelSerializer):
    """Main ModelSerializer for our Product class"""

    collection_name = serializers.StringRelatedField(source="collection")
    price_after_tax = serializers.SerializerMethodField(method_name="calculate_tax")

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
        ]

    def calculate_tax(self, pro):
        return pro.price * Decimal(1.2)
