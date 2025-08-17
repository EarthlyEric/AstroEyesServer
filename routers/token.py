from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from middleware.limiter import limiter
from utils.db import getSession
from utils.db.schemas import UserAccessToken
from utils.jwt import createJWTToken, decodeJWTToken
from models.token import UserRevokeAccessToken, UserRefreshToken

token = APIRouter(
    prefix="/token",
    tags=["Token Management"],
)

@token.post("/revoke")
@limiter.limit("5/minute")
async def cancel_accesstoken(request: Request, data: UserRevokeAccessToken, db: AsyncSession = Depends(getSession)):
    """
    Endpoint for user cancelling an access token.
    Limits:
        - 5 requests per minute.
    Parameters:
        type: application/json
        access_token: The access token to be cancelled.
        device_id: The device ID associated with the token.
    Returns:
        A JSON object containing a success message if the access token is cancelled successfully.
    """
    result = await db.execute(
        select(UserAccessToken).where(
            UserAccessToken.access_token == data.access_token,
            UserAccessToken.device_id == data.device_id
        )
    )
    access_token_record = result.scalar_one_or_none()
    
    if not access_token_record:
        raise HTTPException(status_code=404, detail="Access token is invalid, Maybe already cancelled or expired. Please login again to get a new access token")

    try:
        await db.delete(access_token_record)
        await db.commit()
        
        return {"message": "Access token cancelled successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error cancelling access token: {str(e)}")

@token.post("/refresh")
@limiter.limit("5/minute")
async def refresh_accesstoken(request: Request, data: UserRefreshToken, db: AsyncSession = Depends(getSession)):
    """
    Endpoint for user refreshing an access token.
    Limits:
        - 5 requests per minute.
    Parameters:
        type: application/json
        access_token: The access token to be refreshed.
        device_id: The device ID associated with the token.
    Returns:
        A JSON object containing a new access token if the refresh is successful.
    """
    result = await db.execute(
        select(UserAccessToken).where(
            UserAccessToken.access_token == data.access_token,
            UserAccessToken.device_id == data.device_id
        )
    )
    existing_token = result.scalar_one_or_none()
    
    if not existing_token:
        raise HTTPException(
            status_code=404, 
            detail="Access token not found. Please login again to get a new access token."
        )
    
    if existing_token.expires_at <= datetime.now(timezone.utc):
        try:
            await db.delete(existing_token)
            await db.commit()
        except Exception:
            await db.rollback()
        
        raise HTTPException(
            status_code=401, 
            detail="Access token has expired. Please login again to get a new access token."
        )
    
    time_until_expiry = existing_token.expires_at - datetime.now(timezone.utc)
    
    if time_until_expiry > timedelta(days=1):
        return {
            "message": "Token is still valid, no refresh needed",
            "access_token": data.access_token,
            "expires_at": existing_token.expires_at.isoformat(),
            "time_until_expiry": str(time_until_expiry)
        }
    
    try:
        token_payload = decodeJWTToken(data.access_token)
        user_uuid = token_payload["user_uuid"]
        device_id = token_payload["device_id"]
        
        if device_id != data.device_id:
            raise HTTPException(
                status_code=400,
                detail="Device ID mismatch"
            )
        
        await db.delete(existing_token)
        
        new_access_token = createJWTToken(user_uuid, device_id, expire_days=7)
        new_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        new_token_record = UserAccessToken(
            user_uuid=user_uuid,
            access_token=new_access_token,
            device_id=device_id,
            expires_at=new_expires_at
        )
        
        db.add(new_token_record)
        await db.commit()
        await db.refresh(new_token_record)
        
        return {
            "message": "Access token refreshed successfully",
            "access_token": new_access_token,
            "device_id": device_id,
            "created_at": new_token_record.created_at.isoformat(),
            "expires_at": new_token_record.expires_at.isoformat()
        }
        
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid token format: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error refreshing access token: {str(e)}"
        )