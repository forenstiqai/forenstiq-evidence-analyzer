"""
Configuration file loader and manager
"""
import configparser
from pathlib import Path
from typing import Any, Optional

class ConfigLoader:
    """Load and manage application configuration"""
    
    def __init__(self, config_file='config/settings.ini'):
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        self.load()
    
    def load(self):
        """Load configuration from file"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        self.config.read(self.config_file)
    
    def get(self, section: str, key: str, fallback: Any = None) -> str:
        """Get configuration value"""
        return self.config.get(section, key, fallback=fallback)
    
    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value"""
        return self.config.getint(section, key, fallback=fallback)
    
    def get_float(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get float configuration value"""
        return self.config.getfloat(section, key, fallback=fallback)
    
    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value"""
        return self.config.getboolean(section, key, fallback=fallback)
    
    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
    
    def save(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get_path(self, section: str, key: str) -> Path:
        """Get path from configuration"""
        path_str = self.get(section, key)
        if path_str:
            return Path(path_str)
        return None


# Global config instance
_config = None

def get_config():
    """Get global config instance"""
    global _config
    if _config is None:
        _config = ConfigLoader()
    return _config