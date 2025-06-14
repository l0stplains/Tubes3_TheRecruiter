import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
except ImportError as e:
    print(f"[-] Error importing dotenv: {e}")
    print("[*] Install with: pip install python-dotenv")
    raise

class DatabaseConfig:
    def __init__(self) -> None:
        try:
            env_file = self._find_env_file()
            if env_file:
                load_dotenv(env_file)
        except Exception as e:
            print(f"[-] Error loading .env file: {e}")
            
        try:
            self.host: str = os.getenv('DB_HOST', 'localhost')
            self.port: int = int(os.getenv('DB_PORT', '3306'))
            self.database: str = os.getenv('DB_NAME', 'ats_system')
            self.user: str = os.getenv('DB_USER', 'root')
            self.password: str = os.getenv('DB_PASSWORD', '')

            self.encryption_password: Optional[str] = os.getenv('ENCRYPTION_PASSWORD')
            
        except ValueError as e:
            raise ValueError(f"Invalid database configuration: {e}")
        
        if not all([self.host, self.database, self.user]):
            raise ValueError("Missing required database configuration")
    
    def _find_env_file(self) -> Optional[Path]:
        try:
            current_dir = Path(__file__).parent
            
            env_file = current_dir / '.env'
            if env_file.exists():
                return env_file
            
            for parent in current_dir.parents:
                env_file = parent / '.env'
                if env_file.exists():
                    return env_file
        except Exception:
            pass
        
        return None
    
    def get_connection_params(self) -> Dict[str, Any]:
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password
        }
    
    def get_encryption_password(self) -> Optional[str]:
        return self.encryption_password
    
    def has_encryption_password(self) -> bool:
        return self.encryption_password is not None and len(self.encryption_password.strip()) > 0

_config: Optional[DatabaseConfig] = None

def get_db_config() -> DatabaseConfig:
    global _config
    if _config is None:
        _config = DatabaseConfig()
    print(f"[+] Loaded database config: host={_config.host}, database={_config.database}, user={_config.user}")
    if _config.has_encryption_password():
        print(f"[+] Encryption password configured")
    else:
        print(f"[*] No encryption password configured")
    return _config