from utils.db import init_db
import asyncio

# For development purposes, this script initializes the database.
# It should not be used in production environments.
if __name__ == "__main__":
    asyncio.run(init_db())
    print("Database initialized.")
