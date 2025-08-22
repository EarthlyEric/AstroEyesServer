from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from middleware.limiter import limiter
from utils.db import get_session
from utils.db.schemas import UserRefreshToken
from utils.jwt import create_jwt_token, decode_jwt_token
from models.token import RevokeRefreshToken, RefreshToken, RefreshType

token = APIRouter(
    prefix="/token",
    tags=["Token Management"],
)

@token.post("/revoke")
@limiter.limit("5/minute")
async def cancel_accesstoken(request: Request, data: RevokeRefreshToken, db: AsyncSession = Depends(get_session)):
    """
    Endpoint for user cancelling an access token.
    Limits:
        - 5 requests per minute.
    Parameters:
        type: application/json
        refresh_token: The refresh token to be cancelled.
        device_id: The device ID associated with the token.
    Returns:
        A JSON object containing a success message if the refresh token is cancelled successfully.
    """
    result = await db.execute(
        select(UserRefreshToken).where(
            UserRefreshToken.token == data.refresh_token,
            UserRefreshToken.device_id == data.device_id
        )
    )
    token_record = result.scalar_one_or_none()
    
    if not token_record:
        raise HTTPException(status_code=404, detail="Refresh token is invalid, Maybe already cancelled or expired. Please login again to get a new access token")

    try:
        await db.delete(token_record)
        await db.commit()

        return {"message": "Refresh token cancelled successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error cancelling refresh token: {str(e)}")

@token.post("/refresh")
@limiter.limit("5/minute")
async def refresh_token(request: Request, data: RefreshToken, db: AsyncSession = Depends(get_session)):
    """
    Endpoint for user refreshing an access token.
    Limits:
        - 5 requests per minute.
    Parameters:
        type: application/json
        access_token: The access token to be refreshed.
        refresh_token: The refresh token to be used.
        device_id: The device ID associated with the token.
    Returns:
        A JSON object containing a new access token if the refresh is successful.
    """
    if data.type == RefreshType.ACCESS_TOKEN:
        pass
    elif data.type == RefreshType.REFRESH_TOKEN:
        pass
    