from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from datetime import datetime
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from twilio.rest import Client
import os
import re

from database import SessionLocal, engine, Base
from models import User, Medicine

app = FastAPI()
templates = Jinja2Templates(directory="./templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database Initialization
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully in FastAPI!")
except Exception as e:
    print("❌ FastAPI Database Error:", e)
# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Twilio Credentials
TWILIO_SID = os.getenv("TWILIO_SID", "AC26842caea88726e83f27af3912c0b83f")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "59be7e8982fe2c033f09e41f23e4e21b")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+14178043511")


# Dependency: Get Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Utility Function: Validate Phone Number Format (E.164)
def is_valid_phone_number(phone_number):
    return bool(re.match(r"^\+[1-9]\d{1,14}$", phone_number))


# Home Redirect
@app.get("/")
def home():
    return RedirectResponse(url="/login")


# Register
@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register(name: str = Form(...), email: str = Form(...), password: str = Form(...), phone: str = Form(...), db: Session = Depends(get_db)):
    if not is_valid_phone_number(phone):
        raise HTTPException(status_code=400, detail="Invalid phone number format. Use E.164 (e.g., +1234567890)")
    
    hashed_password = pwd_context.hash(password)
    user = User(name=name, email=email, password=hashed_password, phone=phone)
    db.add(user)
    db.commit()
    return RedirectResponse(url="/login", status_code=303)


# Login
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="user_id", value=str(user.id))
    return response


@app.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("user_id")  # Remove session cookie
    return response
    

# Dashboard
@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    medicines = db.query(Medicine).filter(Medicine.user_id == user.id).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "medicines": medicines})


# Set Medicine Reminder
@app.post("/set-medicine")
def set_medicine(name: str = Form(...), time: str = Form(...), db: Session = Depends(get_db), request: Request = None):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    reminder = Medicine(user_id=int(user_id), name=name, time=time)
    db.add(reminder)
    db.commit()
    return RedirectResponse(url="/dashboard", status_code=303)


# Profile Page
@app.get("/profile")
def profile(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse("profile.html", {"request": request, "user": user})


# Set Emergency Contact
@app.post("/set-emergency")
def set_emergency(emergency_contact: str = Form(...), db: Session = Depends(get_db), request: Request = None):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    if not is_valid_phone_number(emergency_contact):
        raise HTTPException(status_code=400, detail="Invalid phone number format. Use E.164 (e.g., +1234567890)")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.emergency_contact = emergency_contact
    db.commit()
    return RedirectResponse(url="/profile", status_code=303)


@app.post("/toggle-emergency")
def toggle_emergency(request: Request, enabled: bool = Form(...), db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.emergency_enabled = enabled
    db.commit()
    return {"status": "success"}



@app.post("/sos-alert")
async def sos_alert(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.emergency_contact:
        return {"error": "No emergency contact set"}

    if not TWILIO_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        return {"error": "Twilio credentials missing"}

      # Get location from request JSON (frontend should send latitude & longitude)
    request_data = await request.json()
    latitude = request_data.get("latitude")
    longitude = request_data.get("longitude")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    location_info = f"📍 Location: https://www.google.com/maps?q={latitude},{longitude}" if latitude and longitude else "📍 Location: Unknown"

    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
 body=f"🚨 SOS Alert! {user.name} needs help!\n⏰ Time: {timestamp}\n{location_info}",        
     from_=TWILIO_PHONE_NUMBER,
            to=user.emergency_contact
        )
        return {"status": "SOS Sent", "message_sid": message.sid}
    except Exception as e:
        print(f"Twilio Error: {str(e)}")  # Debugging
        return {"error": f"Twilio API error: {str(e)}"}
