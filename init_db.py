from utils.db import initDB
import asyncio

# For development purposes, this script initializes the database.
# It should not be used in production environments.
if __name__ == "__main__":
    asyncio.run(initDB())
    print("Database initialized.")
