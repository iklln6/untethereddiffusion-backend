from pydantic import BaseModel, EmailStr
from typing import Optional







class GenerateRequest(BaseModel):
    pos_prompt: str
    neg_prompt: Optional[str] = ""
    width: Optional[int] = 512
    height: Optional[int] = 512
    sampler: Optional[str] = "euler"
    scheduler: Optional[str] = "normal"
    steps: Optional[int] = 20
    cfg: Optional[float] = 7.5
    clip_skip: Optional[int] = 0
    seed: Optional[int] = None
    checkpoint_model: Optional[str] = "default_model.safetensors"
    batch_size: Optional[int] = 1





class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_premium: bool
    tokens: int

    class Config:
        from_attributes = True # SQLAlchemy 2.x requires this instead of orm_mode

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

