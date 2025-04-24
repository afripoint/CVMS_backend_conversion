from products.models import Plan, Product
from rest_framework import serializers


class ProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "name",
            "description",
            "price",
            "is_plan_based",
            "is_active",
            "action_type",
        )


class PlanSerializers(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = (
            "name",
            "price",
            "is_plan_based",
            "is_active",
            "action_type",
        )
