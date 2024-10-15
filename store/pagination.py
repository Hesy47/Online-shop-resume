from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    page_size = 3


class CollectionPagination(PageNumberPagination):
    page_size = 2
