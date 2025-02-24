# from django.db import models
# from django.utils.crypto import get_random_string
# from accounts.models import CustomUser


# class APIKey(models.Model):
#     key = models.CharField(unique=True, max_length=70, blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"API Key {self.key}"
    
#     def save(self, *args, **kwargs):
#         if not self.key:
#             self.key = APIKey.generate_key()
#         return super().save(*args, **kwargs)

#     @classmethod
#     def generate_key(cls):
#         return get_random_string(32)
