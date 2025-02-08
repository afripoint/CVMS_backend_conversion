from django.db import models
import uuid
from django.utils.text import slugify

from accounts.models import CustomUser


class CACUserVerification(models.Model):
    user = models.ForeignKey(CustomUser, related_name='cac', on_delete=models.CASCADE)
    email = models.EmailField(max_length=254, null=True, blank=True)
    slug = models.CharField(max_length=400, unique=True)
    cac_certificate = models.ImageField(
        upload_to="cac_certificates", default="avartar.png", null=True, blank=True
    )
    status_certificate = models.ImageField(
        upload_to="status_certificates", default="avartar.png", null=True, blank=True
    )
    letter_of_authorization = models.ImageField(
        upload_to="authorization_letter", default="avartar.png", help_text="Signed by Company Secretary or Director", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} cac verification request"
    
    class Meta:
        verbose_name = "CAC verification request"
        verbose_name_plural = "CAC verification requests"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user.phone_number) + str(uuid.uuid4())
        super().save(*args, **kwargs)

        
    
