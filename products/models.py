from django.db import models
from django.utils.text import slugify
import uuid


class Plan(models.Model):
    slug = models.CharField(max_length=250, unique=True,null=True, blank=True, editable=False)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    vin_allocation = models.IntegerField(default=0)
    description = models.TextField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @staticmethod
    def generate_unique_slug(name):
        base_slug = slugify(name)
        unique_slug = base_slug
        counter = 1
        while Plan.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = Plan.generate_unique_slug(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    ACTION_TYPE = (
        ("pay and download", "Pay and Download"),
        ("pay and not download", "Pay and Not Download"),
    )
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=150)
    slug = models.CharField(max_length=250, unique=True, null=True, blank=True, editable=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_plan_based = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    action_type = models.CharField(
        max_length=50, choices=ACTION_TYPE, default="pay and download"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
    
    @staticmethod
    def generate_unique_slug(name):
        base_slug = slugify(name)
        unique_slug = base_slug
        counter = 1
        while Product.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = Product.generate_unique_slug(self.name)
        super().save(*args, **kwargs)


