from twilio.rest import Client
import random
from django.conf import settings

account_sid = settings.OTP_TWILIO_ACCOUNT
auth_token = settings.OTP_TWILIO_AUTH
verify_sid = settings.VERIFY_SID

# Set up Twilio client
client = Client(account_sid, auth_token)

# def generateRandomOTP(x, y):
#     otp = random.randint(x, y)
#     return otp


# Send OTP via SMS
def send_otp_twillo(phone_number, otp):
    message = client.messages.create(
        body=f"Your OTP verification code is: {otp}",
        from_=f"+15855413598",
        to=phone_number,
    )
    print(message.sid)

