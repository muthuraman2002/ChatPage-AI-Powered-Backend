import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
load_dotenv()

FROMEMAIL=os.getenv("FROM_EMAIL")

def send_reset_email(to_email, reset_link):
    subject = "Password Reset Request"
    body = f"Click the link to reset your password: {reset_link}"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] =FROMEMAIL
    msg["To"] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("your_email@example.com", "your_email_password")
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())