from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.utils import verify_password, create_access_token, hash_password
from app.schemas import LoginRequest, TokenResponse, UserResponse, UserCreate, LoginResponse, GenerateRequest
from app.database import get_db
from app.utils import get_current_user
#from sqlalchemy.orm import Session
from app import models
from app.models import User
import os
import requests

from dotenv import dotenv_values

dot_env_vars = dotenv_values("../../.env")



RUNPODS_API_KEY = dot_env_vars['RUNPODS_API_KEY']
RUNPODS_ENDPOINT = dot_env_vars['RUNPODS_ENDPOINT']




router = APIRouter()




@router.get("/check_job/{job_id}")
async def check_job(job_id: str, user=Depends(get_current_user)):
    if not RUNPOD_API_KEY or not RUNPOD_ENDPOINT:
        raise HTTPException(status_code=500, detail="RunPod configuration missing.")
    headers = { "Authorization": f"Bearer {RUNPOD_API_KEY}" }
    url = f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT}/status/{job_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        job_data = response.json()          # <<---- JOB DATA (IMAGE)
        if job_data["status"] == "COMPLETED":
            image_b64 = job_data["output"].get("message")
            img_size = len(image_b64)
            print("Image received: "+str(img_size))
            
        return job_data
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"RunPod error: {str(e)}")


@router.get("/dbtest")
async def test_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return {"user_count":len(users)}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/login",response_model=LoginResponse)
async def login_user(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
       
    access_token = create_access_token({"sub":str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer", "user": user}



@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = hash_password(user.password)
    
    new_user = User(
        email=user.email,
        password_hash=hashed_pw,
        tokens=10  # Give some free tokens
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user



@router.post("/generate")
async def generate_image(
    request: GenerateRequest,
    user: User = Depends(get_current_user)
):
    seed = request.seed or int.from_bytes(os.urandom(2), "big")

    workflow = {
        "input": {
            "workflow": {
                "3": {
                    "inputs": {
                        "add_noise": "enable",
                        "noise_seed": seed,
                        "steps": request.steps,
                        "cfg": request.cfg,
                        "sampler_name": request.sampler,
                        "scheduler": request.scheduler,
                        "start_at_step": request.clip_skip,
                        "end_at_step": 1000,
                        "return_with_leftover_noise": "disable",
                        "model": ["4", 0],
                        "positive": ["6", 0],
                        "negative": ["7", 0],
                        "latent_image": ["5", 0]
                    },
                    "class_type": "KSamplerAdvanced"
                },
                "4": {
                    "inputs": {
                        "ckpt_name": request.checkpoint_model
                    },
                    "class_type": "CheckpointLoaderSimple"
                },
                "5": {
                    "inputs": {
                        "width": request.width,
                        "height": request.height,
                        "batch_size": request.batch_size
                    },
                    "class_type": "EmptyLatentImage"
                },
                "6": {
                    "inputs": {
                        "text": request.pos_prompt,
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "7": {
                    "inputs": {
                        "text": request.neg_prompt,
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "8": {
                    "inputs": {
                        "samples": ["3", 0],
                        "vae": ["4", 2]
                    },
                    "class_type": "VAEDecode"
                },
                "9": {
                    "inputs": {
                        "filename_prefix": "ComfyUI",
                        "images": ["8", 0]
                    },
                    "class_type": "SaveImage"
                }
            }
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {RUNPOD_API_KEY}"
    }

    response = requests.post(f"https://api.runpod.ai/v2/{RUNPOD_ENDPOINT}/run", headers=headers, json=workflow)
 #f"https://104.18.8.221/v2/{RUNPOD_ENDPOINT}/run",
    if response.status_code == 200:
        response_data = response.json()
        job_id = response_data.get('id')
        job_stat = response_data.get('status')
        print('Job ID:\t\t'+str(job_id))
        print('Job Stat:\t'+str(job_stat))
    else:
        return {"error": "RunPod request failed", "details": response.text}
    return response.json()
