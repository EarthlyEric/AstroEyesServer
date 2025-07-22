from fastapi import APIRouter, Request, HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from middleware.limiter import limiter
from utils.db import getSession
from utils.db.schemas import User
from utils.jwt import getUserUUID
from models.user import updateUser, updateUserPassword
 
user = APIRouter(
    prefix="/user",
    tags=["user"],
)

@user.get("/getUser")
@limiter.limit("10/minute")
async def get_user(request: Request, user_uuid: str = Depends(getUserUUID), db: AsyncSession = Depends(getSession)):
    """
    Endpoint to get User information
    """
    result = await db.execute(
        select(User).where(User.uuid == user_uuid)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
 
    return {
        "username": db_user.username,
        "display_name": db_user.display_name,
        "uuid": db_user.uuid,
        "avatar_url": db_user.avatar_url,
        "lang_code": db_user.lang_code,
        "timezone": db_user.timezone,
        "is_online": db_user.is_online,
        "last_online_at": db_user.last_online_at.isoformat(),
        "registered_at": db_user.registered_at.isoformat(),
    }

@user.post("updateUser")
@limiter.limit("5/minute")
async def update_user(request: Request, data: updateUser, user_uuid: str = Depends(getUserUUID), db: AsyncSession = Depends(getSession)):
    result = await db.execute(select(User).where(User.uuid == user_uuid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if data.display_name:
        user.display_name = data.display_name
        await db.commit()
        return {"message": "Display name updated successfully", "display_name": user.display_name}
    
        
@user.post("/updateUserPassword")
@limiter.limit("1/minute")
async def update_user_password(request: Request, data: updateUserPassword, user_uuid: str = Depends(getUserUUID), db: AsyncSession = Depends(getSession)):
    pass
    
@user.get("/getHost")
@limiter.limit("10/minute")
async def get_host(request: Request):
    host = request.headers.get("host")
    return {"host": host}

