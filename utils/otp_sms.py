# otp_sms.py
import os
import random
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone = os.getenv("TWILIO_PHONE")

client = Client(account_sid, auth_token)

def generate_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def send_otp_sms(to_phone: str, otp: str) -> bool:
    try:
        message = client.messages.create(
            body=f"Your OTP code is: {otp}",
            from_=twilio_phone,
            to=to_phone
        )
        return True
    except Exception as e:
        print("Error sending SMS:", e)
        return False
