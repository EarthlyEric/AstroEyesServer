from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from contextlib import asynccontextmanager
from utils.config import config
from utils.db import testDB
from utils.log import logger
from middleware.limiter import limiter

from routers.auth import auth
from routers.user import user
from routers.utils import utils
from routers.token import token

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        if await testDB():
            logger.info("Database connection successful.")
            yield
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise RuntimeError("Database connection failed") from e
    
app = FastAPI(
    title="AstroEyes API",
    version=config.version,
    description="API for AstroEyes",
    docs_url="/docs",
    redoc_url=None,
    debug=False if config.environment == "development" else False,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.get("/")(lambda: {"message": "Welcome to AstroEyes API"})

app.include_router(auth)
app.include_router(token)
app.include_router(user)
app.include_router(utils)


