from django.db import models
import uuid
from django.utils.text import slugify
from django.db import transaction


class Permission(models.Model):
    name = models.CharField(max_length=255)
    permission_code = models.CharField(max_length=150, editable=False, unique=True)
    description = models.TextField(blank=True, null=True)
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

    @classmethod
    def create_default_permissions(cls):
        default_permissions = [
            {
                "name": "Can View Users",
                "description": "Permission to view user details"
            },
            {
                "name": "Can Create Users",
                "description": "Permission to create new users"
            },
            {
                "name": "Can Edit Users",
                "description": "Permission to edit existing users"
            },
            {
                "name": "Can Delete Users",
                "description": "Permission to delete users"
            },
            {
                "name": "Can View Reports",
                "description": "Permission to view reports"
            },
            {
                "name": "Can Create Reports",
                "description": "Permission to create new reports"
            },
            {
                "name": "Can Edit Reports",
                "description": "Permission to edit existing reports"
            },
            {
                "name": "Can Delete Reports",
                "description": "Permission to delete reports"
            },
        ]
        
        with transaction.atomic():
            for perm_data in default_permissions:
                cls.objects.get_or_create(
                    name=perm_data["name"],
                    defaults={"description": perm_data["description"]}
                )


class Department(models.Model):
    department = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    slug = models.CharField(max_length=400, blank=True, null=True, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.department
    
    class Meta:
        verbose_name = "department"
        verbose_name_plural = "departments"
        ordering = ["-department"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.department) + str(uuid.uuid4())
        super().save(*args, **kwargs)

    def get_permissions(self):
        """
        Returns a list of permission codes associated with this department
        """
        return self.permissions.values_list('permission_code', flat=True)

    @classmethod
    def create_default_departments(cls):
        default_departments = [
            {
                "department": "Administration",
                "description": "Administrative department with full system access"
            },
            {
                "department": "Operations",
                "description": "Operations department handling day-to-day activities"
            },
            {
                "department": "Customer Service",
                "description": "Customer service and support department"
            },
            {
                "department": "Finance",
                "description": "Financial operations and management department"
            }
        ]
        
        with transaction.atomic():
            for dept_data in default_departments:
                cls.objects.get_or_create(
                    department=dept_data["department"],
                    defaults={"description": dept_data["description"]}
                )