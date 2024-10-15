from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html
from django.utils.http import urlencode
from django.urls import reverse
from django.contrib.contenttypes.admin import GenericStackedInline
from store import models
from tags import models as tags_models


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "product_count"]
    search_fields = ["title"]
    ordering = ["id"]
    list_per_page = 50

    @admin.display(ordering="product_count")
    def product_count(self, collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )
        return format_html("<a href='{}'>{}</a>", url, collection.product_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(product_count=Count("product"))


class TagsInline(GenericStackedInline):
    model = tags_models.TaggedItem
    extra = 0
    min_num = 0
    max_num = 6
    autocomplete_fields = ["tag"]


class ImagesInline(admin.StackedInline):
    model = models.ProductImage
    extra = 0
    min_num = 0
    max_num = 8


@admin.register(models.Product)
class Product(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "collection",
        "price",
        "last_update",
        "inventory",
        "status",
    ]
    search_fields = ["title"]
    exclude = ["promotions"]
    ordering = ["id"]
    actions = ["clear_inventory"]
    inlines = [TagsInline, ImagesInline]
    list_per_page = 50

    @admin.display(ordering="inventory")
    def status(self, product):
        if product.inventory < 50:
            return "Low"
        return "Ok"

    @admin.action(description="Clear Inventory")
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(
            request, f"{update_count} Items have been cleared", messages.SUCCESS
        )


class OrderFilter(admin.SimpleListFilter):
    """Custom Admin Filter for CustomerAdmin"""

    title = "is_order"
    parameter_name = "is_order"

    def lookups(self, request, model_admin):
        return [("<1", "No"), (">1", "Yes")]

    def queryset(self, request, queryset):
        if self.value() == "<1":
            return queryset.filter(order_count__lt=1)
        elif self.value() == ">1":
            return queryset.filter(order_count__gte=1)


@admin.register(models.Customer)
class Customer(admin.ModelAdmin):
    list_display = [
        "id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "membership",
        "order_count",
    ]
    search_fields = ["first_name", "last_name"]
    list_filter = ["membership", OrderFilter]
    ordering = ["id"]
    list_editable = ["membership"]
    list_per_page = 50

    @admin.display(ordering="order_count")
    def order_count(self, customer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": str(customer.id)})
        )
        return format_html("<a href='{}'>{}</a>", url, customer.order_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(order_count=Count("order"))


class OrderItemInline(admin.StackedInline):
    """Add new product in OrderAdmin panel"""

    model = models.OrderItem
    extra = 0
    min_num = 0
    max_num = 5
    autocomplete_fields = ["product"]


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer",
        "placed_at",
        "payment_status",
    ]
    list_filter = ["payment_status"]
    autocomplete_fields = ["customer"]
    ordering = ["id"]
    inlines = [OrderItemInline]
    list_per_page = 50


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "date", "product", "description"]
    search_fields = ["name"]
    ordering = ["id"]


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    ordering = ["created_at"]


@admin.register(models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["id", "image", "product"]
    ordering = ["id"]
    search_fields = ["product"]
