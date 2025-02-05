import requests
from django.conf import settings
import random


DOJAH_BASE_URL = "https://api.dojah.io/"
DOJAH_APP_ID = "66fa41fac46f1b34e4e2b380"
DOJAH_AUTHORIZATION = "prod_sk_6aStdM0HWJd1N7aMi6SKwchr7"

# create random numbers for OTP
def generateRandomOTP(x, y):
    otp = random.randint(x, y)
    return otp


def verify_nin(nin):
    """
    Calls the Dojah API to verify NIN and fetch user details.
    """
    url = f"{DOJAH_BASE_URL}/api/v1/kyc/nin"
    headers = {
        "AppId": DOJAH_APP_ID,
        "Authorization": DOJAH_AUTHORIZATION,
    }
    params = {"nin": nin}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to verify NIN", "status_code": response.status_code}
