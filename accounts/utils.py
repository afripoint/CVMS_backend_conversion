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