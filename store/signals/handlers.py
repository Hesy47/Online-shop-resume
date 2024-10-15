from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from store import models


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_for_new_user(sender, **kwargs):
    if kwargs["created"]:
        models.Customer.objects.create(user=kwargs["instance"])
