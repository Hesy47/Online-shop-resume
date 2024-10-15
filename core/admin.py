from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
from django.utils.html import format_html
from django.utils.http import urlencode
from django.urls import reverse


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):

    list_display = [
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "status",
        "customer_id",
        "info",
    ]
    ordering = ["id"]

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                ),
            },
        ),
    )

    @admin.display(ordering="is_staff")
    def status(self, user):
        if user.is_staff == True and user.is_superuser == False:
            return "Admin"

        elif user.is_staff == True and user.is_superuser == True:
            return "MasterAdmin"

        else:
            return "User"

    @admin.display(ordering="id")
    def info(self, user):
        url = (
            reverse("admin:store_customer_changelist")
            + "?"
            + urlencode({"user__id": str(user.id)})
        )
        return format_html("<a href='{}'>{}</a>", url, user.customer)
