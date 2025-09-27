# Otp-Based-Authentication-
Otp Based Authentication by Email And Mobile Number Using FastApi 
FastAPI Authentication System (Backend Only)

This is a complete Authentication System built with FastAPI + MySQL.
It allows user Registration (Email / Mobile / Both), OTP Verification, Login, and Password Reset.


---

Features

Register with Email, Mobile number, or both

Verify account with OTP (sent to Email / Mobile)

Login with username, email, or mobile number + password

Forgot password → reset using OTP

If mobile OTP service (Twilio / Fast2SMS) trial ends → show message:
"Due to budget issue, you cannot register with mobile no 😅"



---

Tech Stack

Backend: FastAPI, SQLAlchemy, MySQL

Database: MySQL

OTP:

Email → Free (via Gmail SMTP)

Mobile → Twilio / Fast2SMS (free trial, then paid)




---

Project Structure

backend/
│── main.py          # Entry point
│── auth.py          # Auth routes (register, login, otp, reset)
│── database.py      # Database connection
│── models.py        # SQLAlchemy models
│── schemas.py       # Pydantic schemas
│── utils.py         # Helper functions (OTP, hashing, email, sms)
│── create_tables.py # Create tables
│── .env             # Environment variables
│── requirements.txt # Dependencies


---

Setup Instructions

1. Clone the repo

git clone https://github.com/yourusername/fastapi-auth-backend.git
cd fastapi-auth-backend

2. Create virtual environment

python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3. Install dependencies

pip install -r requirements.txt

4. Create .env file

DATABASE_URL=mysql+mysqlconnector://root:password@localhost/authdb
SECRET_KEY=your_jwt_secret
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
TWILIO_SID=your_twilio_sid
TWILIO_AUTH=your_twilio_auth
TWILIO_PHONE=+1234567890

5. Create database tables

python create_tables.py

6. Run the backend

uvicorn main:app --reload


---

API Endpoints

POST /register → Register new user

POST /verify-otp → Verify OTP and activate account

POST /login → Login with username/email/phone + password

POST /forgot-password → Send OTP for reset password

POST /reset-password → Set new password



---

OTP Testing

In development → OTP will be printed in console and stored in database

In production → OTP will be sent to Email / Mobile



---

Notes

Mobile OTP is free only during Twilio/Fast2SMS trial. After trial ends, users will see:
"Due to budget issue, you cannot register with mobile no 😅"

Email OTP is always free.
