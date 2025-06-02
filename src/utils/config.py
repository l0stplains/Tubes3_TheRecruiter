import os

class DatabaseConfig:
    """Simple database configuration"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 2025))
        self.database = os.getenv('DB_NAME', 'ats_system')
        self.user = os.getenv('DB_USER', 'gongyoo')
        self.password = os.getenv('DB_PASSWORD', 'roulette')
    
    def get_connection_params(self):
        """Get database connection parameters"""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password
        }