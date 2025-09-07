import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client


# send SMS using Twilio
def send_sms(to_number, otp):
    try:
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        client.messages.create(
            body=f"Your OTP is {otp}",
            from_=os.getenv("TWILIO_PHONE"),
            to=to_number
        )
        return True
    except Exception as e:
        print("SMS Error:", e)
        return False

# Send Email using SMTP Gmail
def send_email(to_email, otp):
    try:
        msg = MIMEMultipart()
        msg = MIMEText(f"Your OTP is {otp}")
        msg["Subject"] = "OTP Verification"
        msg["From"] = os.getenv("EMAIL_USER")
        msg["To"] = to_email

        server = smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT")))
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
        server.sendmail(os.getenv("EMAIL_USER"), to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Email Error:", e)
        return False