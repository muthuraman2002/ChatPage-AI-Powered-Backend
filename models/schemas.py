from pydantic import BaseModel

class OTPRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    otp: str
    
class UserCreate(BaseModel):
    name: str
    email: str
    phone : str
    password :str  

class UserVerify(BaseModel):
    name:str
    password:str


class ForgotPassword(BaseModel):
    email:str
    

class PasswordReset(BaseModel):
    token: str
    new_password: str



class ChatRequest(BaseModel):
    message: str
   