from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from redis.asyncio import Redis
from passlib.context import CryptContext
from utils.jwt import createJWTToken
from utils.db import getSession
from utils.db.schemas import User, UserAccessToken
from middleware.limiter import limiter
from models.auth import UserLogin, UserRegister

pwd_context = CryptContext(schemes=["pbkdf2_sha512"], deprecated="auto")

auth = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@auth.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, data: UserLogin, db: AsyncSession = Depends(getSession)):
    """
    Endpoint for user login.
    Parameters:
        username: 8-32 characters, allows only letters, numbers, and underscores.
        password: 8-128 characters, allows letters, numbers, and common special characters.
    Returns:
        A JSON object containing a success message, user UUID, and access token.
    """
    result = await db.execute(select(User).where(User.username == data.username))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if data.password == db_user.password:
        access_token = createJWTToken(db_user.uuid, expire_days=7)
        new_access_token = UserAccessToken(
            user_uuid=db_user.uuid,
            access_token=access_token,
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
            "user_uuid": db_user.uuid,
            "access_token": access_token,
            "expires_at": new_access_token.expires_at.isoformat()
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid Username or Password")

@auth.post("/register")
@limiter.limit("3/minute")
async def register(request: Request, data: UserRegister, db: AsyncSession = Depends(getSession)):
    """
    Endpoint for user registration. \n
    Parameters: \n
        username: 8-32 characters, allows only letters, numbers, and underscores.
        password: 8-128 characters, allows letters, numbers, and common special characters.
        display_name: 1-32 characters.
        invite_code: Optional invite code for registration.
    Returns: \n
        A JSON object containing a success message.
    """
    
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
    

@auth.post("/cancel-accesstoken")
@limiter.limit("5/minute")
async def cancel_accesstoken(request: Request, access_token: str, db: AsyncSession = Depends(getSession), ):
    """
    Endpoint for user logout.
    """
    try:
        result = await db.execute(select(UserAccessToken).where(UserAccessToken.access_token == access_token))
        access_token_record = result.scalar_one_or_none()
        
        if not access_token_record:
            raise HTTPException(status_code=404, detail="Access token not found")
        
        await db.delete(access_token_record)
        await db.commit()
        
        return {"message": "Access token cancelled successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error cancelling access token: {str(e)}")

