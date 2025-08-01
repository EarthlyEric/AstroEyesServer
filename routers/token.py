from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from middleware.limiter import limiter
from utils.db import getSession
from utils.db.schemas import UserAccessToken

token = APIRouter(
    prefix="/token",
    tags=["Token Management"],
)

@token.post("/revoke")
@limiter.limit("5/minute")
async def cancel_accesstoken(request: Request, access_token: str, db: AsyncSession = Depends(getSession), ):
    """
    Endpoint for user cancelling an access token.
    Limits:
        - 5 requests per minute.
    Parameters:
        access_token: The access token to be cancelled.
    Returns:
        A JSON object containing a success message if the access token is cancelled successfully.
    """
    result = await db.execute(
            select(UserAccessToken).where(
                UserAccessToken.access_token == access_token
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
async def refresh_accesstoken(request: Request, access_token: str, db: AsyncSession = Depends(getSession)):
    """
    Endpoint for user refreshing an access token.
    Limits:
        - 5 requests per minute.
    Parameters:
        access_token: The access token to be refreshed.
    Returns:
        A JSON object containing a new access token if the refresh is successful.
    """
    result = await db.execute(
            select(UserAccessToken).where(
                UserAccessToken.access_token == access_token
                )
            )
    access_token = result.scalar_one_or_none()
    if not access_token:
        raise HTTPException(status_code=404, detail="Access token is invalid, Maybe already cancelled or expired. Please login again to get a new access token")

    