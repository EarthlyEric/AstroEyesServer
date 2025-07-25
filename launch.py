if __name__ == "__main__":
    import os
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description="Launch the AstroEyes server.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on.")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on.")
    parser.add_argument("--dev", action="store_true", help="Run in development mode with auto-reload.")
    args = parser.parse_args()

    if args.dev:
        print("Running in development mode...")
        uvicorn.run("app:app", reload=True, log_level="debug")
    else:
        print("Running in production mode...")
        uvicorn.run("app:app", host=args.host, port=args.port, log_level="info")
    