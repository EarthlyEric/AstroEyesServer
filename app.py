from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from utils.config import config
from middleware.limiter import limiter
from routers.auth import auth
from routers.user import user

app = FastAPI(
    title="AstroEyes API",
    version=config.version,
    description="API for AstroEyes",
    docs_url="/docs",
    redoc_url=None,
    debug=False if config.environment == "development" else False,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.get("/")(lambda: {"message": "Welcome to AstroEyes API"})

app.include_router(auth)
app.include_router(user)

