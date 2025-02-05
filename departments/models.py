from django.db import models
import uuid
from django.utils.text import slugify


class Department(models.Model):
    department = models.CharField(max_length=50)
    permissions = models.ManyToManyField("Permission", blank=True)
    slug = models.CharField(max_length=400, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.role
    
    class Meta:
        verbose_name = "department"
        verbose_name_plural = "departments"
        ordering = ["-department"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.role) + str(uuid.uuid4())
        super().save(*args, **kwargs)


class Permission(models.Model):
    name = models.CharField(max_length=255)
    permission_code = models.CharField(max_length=150, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.strip().title()
        if not self.permission_code:
            self.permission_code = self.name.strip().lower().replace(" ", "_")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ["-name"]

