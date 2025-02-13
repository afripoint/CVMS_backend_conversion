from django.db import models
from django.utils.text import slugify
# from accounts.models import CustomUser
import uuid

from accounts.models import CustomUser

class CustomDutyFile(models.Model):
    vin = models.CharField(max_length=50, unique=True, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    vehicle_year = models.CharField(max_length=50, blank=True, null=True)
    engine_type = models.CharField(max_length=50, blank=True, null=True)
    vreg = models.CharField(max_length=50, blank=True, null=True)
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    importer_tin = models.CharField(max_length=50, blank=True, null=True)
    importer_business_name = models.CharField(max_length=500, blank=True, null=True)
    importer_address = models.CharField(max_length=500, blank=True, null=True)
    origin_country = models.CharField(max_length=50, blank=True, null=True)
    hscode = models.CharField(max_length=50, blank=True, null=True)
    sgd_num = models.CharField(max_length=50, blank=True, null=True)
    sgd_date = models.CharField(max_length=50, blank=True, null=True)
    office_cod = models.CharField(max_length=50, blank=True, null=True)
    payment_status = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.brand} with vin number: {self.vin}"
    
    class Meta:
        verbose_name = "vin"
        verbose_name_plural = "vins"
        ordering = ["-vin"]



class CustomDutyFileUploads(models.Model):
    uploaded_by = models.CharField(max_length=250)
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    file_type = models.CharField(max_length=10)
    processed_status = models.BooleanField(default=False)
    slug = models.CharField(max_length=400, blank=True, null=True, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.file_type} was uploaded recently  - {self.uploaded_at}'
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.file.name) + str(uuid.uuid4())

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "customDutyFileUpload"
        verbose_name_plural = "customDutyFileUploads"
        ordering = ["-uploaded_by"]



class VINUpload(models.Model):
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    vins = models.FileField(upload_to='vins/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Vins uploaded by - {self.uploaded_by.first_name} {self.uploaded_by.last_name}'
