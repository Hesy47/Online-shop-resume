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

    class Meta:
        model = models.Product
        fields = [
            "id",
            "title",
            "price",
            "inventory",
            "collection",
            "collection_name",
            "description",
        ]