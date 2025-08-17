import jwt
from datetime import datetime,timezone, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils.config import config
from utils.db import getSession
from utils.db.schemas import UserAccessToken


SECRET_KEY = config.secret_key
ALGORITHM = "HS256"

security = HTTPBearer()

def createJWTToken(uuid: str, device_id: str, expire_days: int) -> str:
    payload = {
        "user_uuid": uuid,
        "device_id": device_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=expire_days)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decodeJWTToken(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    except Exception as e:
        raise ValueError(f"An error occurred while decoding the token: {str(e)}")

def verifyJWTTokenFromLocal(token: str) -> bool:
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
    except Exception as e:
        raise ValueError(f"An error occurred while verifying the token: {str(e)}")
    
async def verifyJWTTokenFromDatabase(token: str, db: AsyncSession) -> bool:
    try:
        user_uuid = decodeJWTToken(token)["user_uuid"]
    except Exception:
        return False

    try:
        result = await db.execute(
            select(UserAccessToken).where(UserAccessToken.access_token == token)
        )
        access_token = result.scalar_one_or_none()
        
        if (
            access_token 
            and access_token.user_uuid == user_uuid 
            and access_token.expires_at > datetime.now(timezone.utc)
        ):
            return True
        
        if access_token and access_token.expires_at <= datetime.now(timezone.utc):
            try:
                await db.delete(access_token)
                await db.commit()
            except Exception:
                pass
            return False
    except Exception:
        pass

    return False

async def getUserUUID(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(getSession)) -> str:
    if verifyJWTTokenFromLocal(credentials.credentials) and await verifyJWTTokenFromDatabase(credentials.credentials, db):
        return decodeJWTToken(credentials.credentials)["user_uuid"]
    else:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired token."
        )