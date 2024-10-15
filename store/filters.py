from django_filters.rest_framework import FilterSet
from store import models


class ProductFilter(FilterSet):
    class Meta:
        model = models.Product
        fields = {
            "collection_id": ["exact"],
            "price": ["gte", "lte"],
        }
