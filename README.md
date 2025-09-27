# 🔐 FastAPI Authentication System (Backend Only)

This project is a **User Authentication System** built with **FastAPI + MySQL**.  
It supports **Registration, OTP Verification, Login, and Password Reset**.  

---

## ✨ Features

- **Register**  
  - With Email  
  - With Mobile Number  
  - Or with both  

- **Verify Account**  
  - OTP sent to Email or Mobile  

- **Login**  
  - Using Username  
  - Or Email  
  - Or Mobile Number  
  - With Password  

- **Forgot Password**  
  - Receive OTP for reset  
  - Set new password  

- **Free Fallback**  
  - If SMS OTP trial ends → system shows:  
    > "Due to end of trail, you cannot register with mobile no "  

---

## 🛠 Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic  
- **Database**: MySQL  
- **OTP Services**:  
  - 📧 Email → Free (via Gmail SMTP)  
  - 📱 Mobile → Twilio / Fast2SMS (free trial, then paid)  

---

## 📂 Project Structure

backend/ │── main.py          # Entry point<
         │── auth.py          # Auth routes (register, login, otp, reset)
         │── database.py      # Database connection 
         │── models.py        # SQLAlchemy models 
         │── schemas.py       # Pydantic schemas 
         │── utils.py         # Helper functions (OTP, hashing, email, sms) 
         │── create_tables.py # Create tables 
         │── .env             # Environment variables 
         │── requirements.txt # Dependencies

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/nitin798563/Otp-Based-Authentication-.git
cd Otp-Based-Authentication

2. Create Virtual Environment

python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3. Install Dependencies

pip install -r requirements.txt

4. Configure Environment Variables

Create a .env file in backend/:

DATABASE_URL=mysql+mysqlconnector://root:password@localhost/authdb
SECRET_KEY=your_jwt_secret

# Email OTP (free)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password

# Mobile OTP (Twilio / Fast2SMS)
TWILIO_SID=your_twilio_sid
TWILIO_AUTH=your_twilio_auth
TWILIO_PHONE=+1234567890

5. Create Database Tables

python create_tables.py

6. Run the Backend

uvicorn main:app --reload


---

📡 API Endpoints

🔹 Register

POST /register
Registers a new user with Email / Mobile / Both

🔹 Verify OTP

POST /verify-otp
Verify OTP and activate user account

🔹 Login

POST /login
Login with username, email, or mobile number + password

🔹 Forgot Password

POST /forgot-password
Send OTP to reset password

🔹 Reset Password

POST /reset-password
Set a new password after OTP verification


---

🧪 OTP Handling

Development Mode

OTP is printed in the console

Saved in the database


Production Mode

OTP is sent to Email or Mobile




---

⚠️ Notes

📱 Mobile OTP → free only during Twilio/Fast2SMS trial

After trial:

> "Due to budget issue, you cannot register with mobile no "




📧 Email OTP → always free & unlimited
