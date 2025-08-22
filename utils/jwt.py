import jwt
from datetime import datetime,timezone, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils.config import config
from utils.db import get_session
from utils.db.schemas import UserRefreshToken


SECRET_KEY = config.secret_key
ALGORITHM = "HS256"

security = HTTPBearer()

def create_refresh_token_payload(uuid: str, device_id: str) -> dict:
    payload = {
        "user_uuid": uuid,
        "device_id": device_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=14)
    }
    return payload

def create_access_token_payload(uuid: str, refresh_token_uuid:str, device_id: str) -> dict:
    payload = {
        "user_uuid": uuid,
        "device_id": device_id,
        "refresh_token_uuid": refresh_token_uuid,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=1)
    }
    return payload

def create_jwt_token(payload:dict) -> str:
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    except Exception as e:
        raise ValueError(f"An error occurred while decoding the token: {str(e)}")

def verify_jwt_token(token: str) -> bool:
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
    except Exception as e:
        raise ValueError(f"An error occurred while verifying the token: {str(e)}")
    
async def verify_jwt_token_db(token: str, db: AsyncSession) -> bool:
    try:
        user_uuid = decode_jwt_token(token)["user_uuid"]
    except Exception:
        return False

    try:
        result = await db.execute(
            select(UserRefreshToken).where(UserRefreshToken.token == token)
        )
        token = result.scalar_one_or_none()
        
        if (
            token 
            and token.user_uuid == user_uuid 
            and token.expires_at > datetime.now(timezone.utc)
        ):
            return True
        
        if token and token.expires_at <= datetime.now(timezone.utc):
            try:
                await db.delete(token)
                await db.commit()
            except Exception:
                pass
            return False
    except Exception:
        pass

    return False

async def get_user_uuid(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if verify_jwt_token(credentials.credentials):
        return decode_jwt_token(credentials.credentials)["user_uuid"]
    else:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired token."
        )