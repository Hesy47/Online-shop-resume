from django.db import models
from django.contrib import admin
from django.core.validators import MinValueValidator
from django.conf import settings
from uuid import uuid4


class Promotions(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        "Product", on_delete=models.SET_NULL, null=True, related_name="+", blank=True
    )

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(default="-")
    description = models.TextField()
    price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(1)]
    )
    inventory = models.PositiveIntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(Promotions)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    image = models.ImageField(upload_to="store/images")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )


class Customer(models.Model):
    MEMBER_SHIP_CHOICES = [
        ("G", "Gold"),
        ("S", "Silver"),
        ("B", "Bronze"),
    ]

    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    membership = models.CharField(
        max_length=1, choices=MEMBER_SHIP_CHOICES, default="B"
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @admin.display(ordering="user__first_name")
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering="user__last_name")
    def last_name(self):
        return self.user.last_name

    @admin.display(ordering="user__email")
    def email(self):
        return self.user.email


class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("P", "Pending"),
        ("C", "Complete"),
        ("F", "Failed"),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default="P"
    )
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)


class OrderItem(models.Model):
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_item_set"
    )

    class Meta:
        permissions = [
            ("cancel_order", "Can Cancel Order"),
        ]


class Address(models.Model):
    street = models.CharField(max_length=225)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

    class Meta:
        unique_together = [["cart", "product"]]


class Review(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )

    def __str__(self) -> str:
        return self.name
