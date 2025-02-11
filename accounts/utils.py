import requests
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import random



# create random numbers for OTP
def generateRandomOTP(x, y):
    otp = random.randint(x, y)
    return otp


# custom token geneerator that expires
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}"
    
# GET CLIENT id
def get_client_ip(request):
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

# GET USER AGENT 
def get_user_agent(request):
    """Extract user agent from request."""
    return request.META.get("HTTP_USER_AGENT", "Unknown")
