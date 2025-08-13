from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models.db import SessionLocal, engine,Base
from models.usermodel import User
from models.otp_model import OTPLog
from models.schemas import UserCreate,OTPRequest,OTPVerify,UserVerify,PasswordReset,ChatRequest
from crud import create_user,get_users
from utils.tockenManager import get_current_user,authenticate_user,create_access_token
from utils.otp_sms import generate_otp, send_otp_sms
from utils.mail_sender import send_reset_email
from jose import jwt
import os
from dotenv import load_dotenv
from transformers import pipeline


MODEL_NAME = "microsoft/DialoGPT-small"
chat_pipeline = pipeline(
    "text-generation",
    model=MODEL_NAME,
    max_new_tokens=128,
    do_sample=True,
    temperature=0.7
)

Base.metadata.create_all(bind=engine)
# UserCreate.Base.metadata.create_all(bind=engine)

app = FastAPI()



# Allowed origins (use "*" to allow all, or list specific origins)
origins = [
    "http://localhost:5173",  # React/Vite frontend
    "http://127.0.0.1:5173",
   
]

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # accepts list or ["*"]
    allow_credentials=True,
    allow_methods=["*"],  # or ["GET", "POST", "PUT", ...]
    allow_headers=["*"],
)
load_dotenv()
SECRET_KEY =os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/')
def rootPage ():
    
    return "FAST API Running Successfully in 8000"

@app.post("/send-otp/")
def send_otp(data: OTPRequest, db: Session = Depends(get_db)):
    otp = generate_otp()
    print(otp)
    success = send_otp_sms(data.phone, otp)

    log = OTPLog(
        phone=data.phone,
        otp=otp,
        status="sent" if success else "failed"
    )
    db.add(log)
    db.commit()

    if success:
        return {"message": "OTP sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

@app.post("/verify-otp/")
def verify_otp(data: OTPVerify, db: Session = Depends(get_db)):
    otp_log = (
        db.query(OTPLog)
        .filter(OTPLog.phone == data.phone)
        .order_by(OTPLog.created_at.desc())
        .first()
    )

    if not otp_log or otp_log.otp != data.otp:
        # Optional: log failed attempt
        log = OTPLog(phone=data.phone, otp=data.otp, status="invalid")
        db.add(log)
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Optional: mark as verified
    otp_log.status = "verified"
    db.commit()

    return {"message": "OTP verified"}

@app.post("/signup")
def signUp(user: UserCreate, db: Session = Depends(get_db)):
    print(user)
    db_user = create_user(db=db, user_data=user)
    if not db_user:
        raise HTTPException(status_code=400, detail="User could not be created")
    return {"message": "Sign up successfully", "user": db_user}

@app.post("/login")
def login(form_data: UserVerify, db: Session = Depends(get_db)):
    print("form_data",form_data)
    user = authenticate_user( db,form_data.name, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.name})
    return {"access_token": access_token, "token_type": "bearer"}



# Protected route
@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    print(current_user,130)
    return {"username": current_user["username"]}

# Token endpoint
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# ...existing code...


@app.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Generate reset token
    reset_token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm=ALGORITHM)
    reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
    send_reset_email(user.email, reset_link)
    return {"message": "Password reset email sent"}


@app.post("/reset-password")
def reset_password(data: PasswordReset, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password = data.new_password
    db.commit()
    return {"message": "Password reset successful"}




@app.post("/chat")
def chat(request: ChatRequest):
    print(request)
    response = chat_pipeline(request.message)
    # response = [{
    #     "generated_text":"Hi dude"
    # }]
    # The response is a list of dicts with 'generated_text'
    return {"response": response[0]["generated_text"]}
# ...existing code...
