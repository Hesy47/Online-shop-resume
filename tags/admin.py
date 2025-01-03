from django.contrib import admin
from tags import models


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "label"]
    search_fields = ["label"]
    ordering = ["label"]
