from django.db import models
from django.utils.text import slugify

# from accounts.models import CustomUser
import uuid
import qrcode
import base64
from io import BytesIO
from qrcode.image.pil import PilImage
from django.db import models
from django.utils.timezone import now

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
    file = models.FileField(upload_to="uploads/")
    file_type = models.CharField(max_length=10)
    processed_status = models.BooleanField(default=False)
    slug = models.CharField(max_length=400, blank=True, null=True, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_type} was uploaded recently  - {self.uploaded_at}"

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
    vins = models.FileField(upload_to="vins/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vins uploaded by - {self.uploaded_by.first_name} {self.uploaded_by.last_name}"


class VinSearchHistory(models.Model):
    user = models.ForeignKey(
        CustomUser, related_name="user_search_history", on_delete=models.CASCADE
    )
    vin = models.ForeignKey(
        CustomDutyFile,
        related_name="search_history",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    slug = models.CharField(max_length=150, unique=True)
    status = models.TextField(default="Successful")
    qr_code_binary = models.BinaryField(null=True, blank=True)
    cert_num = models.CharField(max_length=150, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_qr_code(self):
        vin_value = self.vin.vin if self.vin else "Not available"
        payment_status = self.vin.payment_status if self.vin else "Unknown"
        qr_data = f"VIN: {vin_value}, payment_status: {payment_status}, date_created: {self.created_at}"
        img = qrcode.make(qr_data, image_factory=PilImage)

        qr_image = BytesIO()
        img.save(qr_image, format="PNG")
        self.qr_code_binary = qr_image.getvalue()

    # def update_status_if_needed(self):
    #     """
    #     Updates status if more than 48 hours have passed.
    #     """
    #     time_elapsed = now() - self.created_at
    #     if (
    #         "Invalid or uncleared" in self.status_message
    #         and time_elapsed.total_seconds() >= 172800
    #     ):
    #         self.status_message = "Car not duly registered, contact support."

    #     if "Error fetching" in self.status_message and time_elapsed.total_seconds() >= 172800:
    #         self.status_message = "Car not duly registered, contact support."
            
            
    #     self.save()

    def save(self, *args, **kwargs):
        if not self.cert_num:
            vin_slug = slugify(self.vin.vin)[:5] if self.vin else "NO-VIN"
            self.cert_num = self.cert_no = (
                f"CERT-NO/{vin_slug}-{str(uuid.uuid4())[:10]}"
            )
        if not self.qr_code_binary:
            self.generate_qr_code()

        if not self.slug:
            self.slug = slugify(self.user.first_name) + str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        vin = self.vin.vin if self.vin else "No vin available for this record"
        return f"VIN Search History for {vin} at {self.created_at}"


class SupportTicket(models.Model):
    ISSUE_TYPE_CHOICES = (
        ('vin not found'), ('Vin Not Found')
    )
    STATUS_CHOICES = (
        ('resolved', 'Resolved'),
        ('unresolved', 'Unresolved'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='support')
    vin = models.CharField(max_length=50)
    slug = models.CharField(max_length=150, unique=True)
    issue_type = models.CharField(max_length=50)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="resolved")
    attachement =  models.FileField(upload_to="attachement/", max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.first_name} raised a complained ticket'
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.vin) + str(uuid.uuid4())

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "SupportTicket"
        verbose_name_plural = "SupportTickets"
        ordering = ["-created_at"]
    