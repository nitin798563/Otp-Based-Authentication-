from fastapi import APIRouter, HTTPException #for creating routes and handling errors
from pydantic import BaseModel, EmailStr, field_validator #for request validation(EmailStr ensures valid email)

from database import get_connection #To connect with the databse
import bcrypt, jwt, os, random, string #for password hashing, JWT tokens, envs vars, OTP generation
from datetime import datetime, timedelta #for handling time and expiry
from typing import Optional
from utils import send_sms, send_email

router = APIRouter() #used to group all the routes

            #   JWT Settings
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 30))

# ----------- Schemas(for request body validation) -------------
class Register(BaseModel): #for Register API
    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    repassword: str

    @field_validator("email", "phone",mode="after")
    def at_least_one(cls, v, info):
        values = info.data
        if not(v or values.get("email") or values.get("phone")):
            raise ValueError("Either email or phone required")
        return v

class Login(BaseModel): #for Login API
    identifier: str    #username/email/phone
    password: str

class OTPVerify(BaseModel): #for otp verification
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    otp: str

class ForgotPassword(BaseModel): #for Forgot password
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class ResetPassword(BaseModel): #for Reset password
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    otp: str
    new_password: str
    re_password: str

# ----------- Utility Functions -------------
def create_jwt(data: dict): #Function to create JWT token
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES) #set expiry time
    data.update({"exp": expire}) #Add expiry into token data
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM) #Return encoded JWT token

def generate_otp(): #Function to generate OTP
    return ''.join(random.choices(string.digits, k=6)) # Returns a 6-digit random number as OTP

# ----------- Routes -------------

@router.post("/register")
def register(user: Register): #check if password and confirm password match
    if user.password != user.repassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if not user.email and not user.phone:
        raise HTTPException(status_code=400, detail="Email or phone required")

    conn = get_connection() #Get database connection
    cur = conn.cursor(dictionary=True)

    #check if user already exists(by email,phone or username)
    cur.execute("SELECT * FROM users WHERE email=%s OR phone=%s OR username=%s",
                (user.email, user.phone, user.username))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())#hashed the password before saving
    #Insert new user into database
    cur.execute("INSERT INTO users (username, email, phone, password) VALUES (%s,%s,%s,%s)",
                (user.username, user.email, user.phone, hashed))
    conn.commit()
    user_id = cur.lastrowid #Get the new user ID
    
    #generate OTP and save into database
    otp = generate_otp()
    cur.execute("INSERT INTO otps (user_id, otp) VALUES (%s,%s)", (user_id, otp))
    conn.commit()
    
    #👇This is for testing purpose
    # return{"msg":"Registered successfully, verify OTP", "OTP_for_testing": otp}

    sent = False
    
    #Email Service always enabled
    if user.email:
        sent = send_email(user.email, otp) 
        
    #Mobile service is only work when SMS_ENABLED is true in .env
    if user.phone:
        if os.getenv("SMS_ENABLED","false").lower == "true":
            sent = send_sms(user.phone, otp) or sent
        else: #IF disable, then direct return👇
            return {
                "msg": "Due to budget issue,mobile OTP service is disabled.Please use Email"
            }
    

    if not sent:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

    return {"msg": "Registered successfully, OTP sent"}

@router.post("/verify-otp") #verify otp route
def verify_otp(data: OTPVerify):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # find user by email or phone
    if data.email:
        cur.execute("SELECT * FROM users WHERE email=%s", (data.email,))
    elif data.phone:
        cur.execute("SELECT * FROM users WHERE phone=%s", (data.phone,))
    else:
        raise HTTPException(status_code=400, detail="Email or phone required")

    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    #Get the latest OTP for this user
    cur.execute("SELECT * FROM otps WHERE user_id=%s ORDER BY created_at DESC LIMIT 1", (user["id"],))
    otp_entry = cur.fetchone()
    if not otp_entry or otp_entry["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    #If OTP is correct, mark the user as verified
    cur.execute("UPDATE users SET is_verified=TRUE WHERE id=%s", (user["id"],))
    conn.commit()
    return {"msg": "Account verified successfully"}

@router.post("/login") #login route
def login(data: Login):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    # find user by email or phone or username
    cur.execute("SELECT * FROM users WHERE username=%s OR email=%s OR phone=%s",
                (data.identifier, data.identifier, data.identifier))
    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user["is_verified"]:
        raise HTTPException(status_code=403, detail="Account not verified")
    
    # check if password is correct
    if not bcrypt.checkpw(data.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=400, detail="Invalid credentials")
   
    #create a JWT token and return it 
    token = create_jwt({"sub": user["id"]})
    return {"access_token": token}

@router.post("/forgot-password") #forgot password route
def forgot_password(data: ForgotPassword):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    # find user by email or phone
    if data.email:
        cur.execute("SELECT * FROM users WHERE email=%s", (data.email,))
    elif data.phone:
        cur.execute("SELECT * FROM users WHERE phone=%s", (data.phone,))
    else:
        raise HTTPException(status_code=400, detail="Email or phone required")

    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    #Generate OTP and save it in the database
    otp = generate_otp()
    cur.execute("INSERT INTO otps (user_id, otp) VALUES (%s,%s)", (user["id"], otp))
    conn.commit()
    
    #👇This is for testing purpose
    # return{"msg":"Registered successfully, verify OTP", "OTP_for_testing": otp}

    sent = False
    if user["phone"]:
        sent = send_sms(user["phone"], otp)
    if user["email"]:
        sent = send_email(user["email"], otp) or sent

    if not sent:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

    return {"msg": "OTP sent successfully"}

@router.post("/reset-password") #Reser Password Route
def reset_password(data: ResetPassword):
    #Check if new password amd confirm password match
    if data.new_password != data.re_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
 
    # find user by email or phone
    if data.email:
        cur.execute("SELECT * FROM users WHERE email=%s", (data.email,))
    elif data.phone:
        cur.execute("SELECT * FROM users WHERE phone=%s", (data.phone,))
    else:
        raise HTTPException(status_code=400, detail="Email or phone required")

    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    #verify the latest otp
    cur.execute("SELECT * FROM otps WHERE user_id=%s ORDER BY created_at DESC LIMIT 1", (user["id"],))
    otp_entry = cur.fetchone()
    if not otp_entry or otp_entry["otp"] != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    #Hash new password and update it in the database
    hashed = bcrypt.hashpw(data.new_password.encode(), bcrypt.gensalt())
    cur.execute("UPDATE users SET password=%s WHERE id=%s", (hashed, user["id"]))
    conn.commit()
    return {"msg": "Password reset successfully"}