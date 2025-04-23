from django.contrib import admin

from products.models import Product


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "is_plan_based",
        "is_active",
    )
    list_display_links = (
        "name",
        "price",
    )

admin.site.register(Product, ProductAdmin)
