from fastapi import APIRouter, Request
from middleware.limiter import limiter

utils = APIRouter(
    prefix="/utils",
    tags=["Utils"],
)

@utils.get("/getHostname")
@limiter.limit("30/minute")
async def get_hostname(request: Request):
    """
    Endpoint to get the hostname of the server.
    Limits:
        - 30 requests per minute.
    Returns:
        A JSON object containing the hostname.
    """
    hostname = request.headers.get("host")
    return {"hostname": hostname}