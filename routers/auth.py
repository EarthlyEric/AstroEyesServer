from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from middleware.limiter import limiter
from utils.jwt import createJWTToken
from utils.db import getSession
from utils.db.schemas import User, UserAccessToken
from models.auth import userLogin, userRegister

pwd_context = CryptContext(schemes=["pbkdf2_sha512"], deprecated="auto")

auth = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@auth.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, data: userLogin, db: AsyncSession = Depends(getSession)):
    """
    Endpoint for user login.
    Limits:
        - 3 requests per minute.
    Parameters:
        type: application/json
        username: 8-32 characters, allows only letters, numbers, and underscores.
        password: 8-128 characters, allows letters, numbers, and common special characters.
        device_id: Unique identifier for the user's device, such as Android Device ID (16), ios UUID(40).
    Returns:
        A JSON object containing a success message, user UUID, and access token.
    """

    result = await db.execute(
        select(User).where(
            User.username == data.username
            )
        )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if data.password == user.password:
        result = await db.execute(
            select(UserAccessToken).where(
                UserAccessToken.user_uuid == user.uuid,
                UserAccessToken.device_id == data.device_id
            )
        )
        existing_token = result.scalar_one_or_none()
        
        if existing_token and existing_token.expires_at > datetime.now(timezone.utc):
            return {
                "message": "Login successful",
                "user_uuid": user.uuid,
                "access_token": existing_token.access_token,
                "device_id": existing_token.device_id,
                "created_at": existing_token.created_at.isoformat(),
                "expires_at": existing_token.expires_at.isoformat()
            }
        elif existing_token:
            try:
                await db.delete(existing_token)
                await db.commit()
            except Exception as e:
                await db.rollback()
                raise HTTPException(status_code=400, detail=f"Error on deleting expired access token: {str(e)}")

        access_token = createJWTToken(user.uuid, data.device_id, expire_days=7)
        new_access_token = UserAccessToken(
            user_uuid=user.uuid,
            access_token=access_token,
            device_id=data.device_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.add(new_access_token)
        try:
            await db.commit()
            await db.refresh(new_access_token)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Error on creating access token: {str(e)}")
        
        return {
            "message": "Login successful",
            "user_uuid": user.uuid,
            "access_token": access_token,
            "device_id": new_access_token.device_id,
            "created_at": new_access_token.created_at.isoformat(),
            "expires_at": new_access_token.expires_at.isoformat()
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid Username or Password")

@auth.post("/register")
@limiter.limit("3/minute")
async def register(request: Request, data: userRegister, db: AsyncSession = Depends(getSession)):
    """
    Endpoint for user registration. 
    Limits:
        - 3 requests per minute.
    Parameters: 
        type: application/json
        username: 8-32 characters, allows only letters, numbers, and underscores.
        password: 8-128 characters, allows letters, numbers, and common special characters.
        display_name: 1-32 characters.
        invite_code: Optional invite code for registration.
    Returns: 
        A JSON object containing a success message.
    """
    result = await db.execute(
        select(User).where(
            User.username == data.username
        )
    )
    user = result.scalar_one_or_none()
    
    if user:
        raise HTTPException(status_code=409, detail="Username already exists")
    
    new_user = User(
        username=data.username,
        password=data.password,
        display_name=data.display_name
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")
    
    return {"message": "Registration successful", "uuid": new_user.uuid}