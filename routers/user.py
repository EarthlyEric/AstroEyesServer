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
    Parameters:
        No parameters required, user UUID is obtained from JWT token.
    Returns:
        A JSON object containing user information such as username, display name, UUID, avatar URL,
    """
    result = await db.execute(
        select(User).where(User.uuid == user_uuid)
    )
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
 
    return {
        "uuid": db_user.uuid,
        "username": db_user.username,
        "display_name": db_user.display_name,
        "avatar_url": db_user.avatar_url,
        "is_online": db_user.is_online,
        "last_online_at": db_user.last_online_at.isoformat(),
        "registered_at": db_user.registered_at.isoformat(),
    }

@user.post("/updateUser")
@limiter.limit("5/minute")
async def update_user(request: Request, data: updateUser, user_uuid: str = Depends(getUserUUID), db: AsyncSession = Depends(getSession)):
    """
    Endpoint to update User information
    Parameters:
        display_name: Optional, 1-32 characters, the new display name for the user
    Returns:
        A JSON object containing a success message and the updated display name if it was changed.
    Raises:
        HTTPException: If the user is not found or if the display name is not provided.
    """
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
    result = await db.execute(select(User).where(User.uuid == user_uuid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if data.old_password and data.new_password and data.old_password.strip() and data.new_password.strip():
        if user.password != data.old_password:            
            raise HTTPException(status_code=400, detail="Old password is incorrect")
        
        user.password = data.new_password
        await db.commit()
        return {"message": "Password updated successfully"}
    
    raise HTTPException(status_code=400, detail="Invalid request data")


