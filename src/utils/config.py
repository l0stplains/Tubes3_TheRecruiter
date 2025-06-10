import os
from pathlib import Path
from dotenv import load_dotenv

class DatabaseConfig:
    def __init__(self): # load env
        env_file = self._find_env_file()
        if env_file:
            load_dotenv(env_file)
        
        # Database configuration
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.database = os.getenv('DB_NAME', 'ats_system')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        
        if not all([self.host, self.database, self.user]):
            raise ValueError("Missing required database configuration")
    
    def _find_env_file(self):
        current_dir = Path(__file__).parent
        
        env_file = current_dir / '.env'
        if env_file.exists():
            return env_file
        
        for parent in current_dir.parents:
            env_file = parent / '.env'
            if env_file.exists():
                return env_file
        
        return None
    
    def get_connection_params(self):
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password
        }

_config = None

def get_db_config():
    global _config
    if _config is None:
        _config = DatabaseConfig()
    return _config