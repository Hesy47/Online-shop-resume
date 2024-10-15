from rest_framework import serializers
from store import models
from decimal import Decimal


class CollectionSimpleSerializer(serializers.Serializer):
    """Simple serializer for our Collection"""

    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)


class ProductSimpleSerializer(serializers.Serializer):
    """Simple serializer for our Product views"""

    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    unit_price = serializers.DecimalField(
        max_digits=6, decimal_places=2, source="price"
    )
    price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax")
    collection_name = serializers.StringRelatedField(source="collection")
    collection_number = serializers.PrimaryKeyRelatedField(
        queryset=models.Collection.objects.all(),
        source="collection",
    )
    collection_link = serializers.HyperlinkedRelatedField(
        queryset=models.Collection.objects.all(),
        view_name="get_collection_detail",
        source="collection",
    )
    collection = CollectionSimpleSerializer()

    def calculate_tax(self, pro):
        return pro.price * Decimal(1.2)


class CollectionSerializer(serializers.ModelSerializer):
    """Main ModelSerializer for our Collection class"""

    product_count = serializers.IntegerField()

    class Meta:
        model = models.Collection
        fields = ["id", "title", "product_count"]


class ProductSerializer(serializers.ModelSerializer):
    """Main ModelSerializer for our Product class"""

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

    collection_name = serializers.StringRelatedField(source="collection")
