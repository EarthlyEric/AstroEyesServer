if __name__ == "__main__":
    import os
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description="Launch the AstroEyes server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on.")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on.")
    args = parser.parse_args()
    
    if os.getenv("ENVIRONMENT") == "development":
        uvicorn.run("app:app", reload=True, log_level="debug")
    else:
        uvicorn.run("app:app", host=args.host, port=args.port, log_level="info")
    