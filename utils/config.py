import os

class Config:
    def __init__(self):
        with open("version") as file:
            self.version = file.read().strip()
        self.environment = os.getenv("ENVIRONMENT", "production")
        self.secret_key = str(os.getenv("SECRET_KEY"))

        
        self.db_user = os.getenv("DB_USER", "astroeyes")
        self.db_password = os.getenv("DB_PASSWORD", "astroeyes")
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = int(os.getenv("DB_PORT", 5432))
        self.db_database = os.getenv("DB_DATABASE", "astroeyes_db")
        
        self.db_connect_uri = f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_database}"
        
config = Config()         