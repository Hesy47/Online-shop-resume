from django.urls import path
from store import views

urlpatterns = [
    path("hi/", views.hi_rest_framework),
    path("hi/<int:id>/", views.hi_rest_framework_detail),

    path("pro/", views.get_product_list),
    path("pro/<int:id>/", views.get_product_details),
    path("pro/opt/<int:id>/", views.get_product_details_optimized),
    path("co/<int:pk>/", views.get_collection_detail, name="get_collection_detail"),

    path("product/", views.product_list),
    path("product/<int:pk>/", views.product_detail),
    path("collection/", views.collection_list),
    path("collection/<int:pk>/", views.collection_detail),
]
