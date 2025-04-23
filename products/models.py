from django.db import models
from django.utils.text import slugify
import uuid


class Product(models.Model):
    ACTION_TYPE = (
        ("pay and download", "Pay and Download"),
        ("pay and not download", "Pay and Not Download"),
    )
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=150)
    slug = models.CharField(max_length=250, unique=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    is_plan_based = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    action_type = models.CharField(
        max_length=50, choices=ACTION_TYPE, default="pay and download"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + str(uuid.uuid4())
