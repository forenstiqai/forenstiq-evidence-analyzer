"""
Logging configuration and utility functions
"""
import logging
import logging.config
from pathlib import Path
from datetime import datetime

class ForenstiqLogger:
    """Centralized logging for Forenstiq application"""
    
    _logger = None
    
    @classmethod
    def get_logger(cls, name='forenstiq'):
        """Get or create logger instance"""
        if cls._logger is None:
            cls._setup_logging()
        return logging.getLogger(name)
    
    @classmethod
    def _setup_logging(cls):
        """Setup logging configuration"""
        # Create logs directory
        log_dir = Path('./logs')
        log_dir.mkdir(exist_ok=True)
        
        # Load logging config
        config_file = Path('./config/logging.conf')
        if config_file.exists():
            logging.config.fileConfig(config_file)
        else:
            # Fallback to basic config
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_dir / 'forenstiq.log'),
                    logging.StreamHandler()
                ]
            )
        
        cls._logger = logging.getLogger('forenstiq')
        cls._logger.info('Logging system initialized')
    
    @classmethod
    def log_case_action(cls, case_id, action, details=None):
        """Log case-related actions"""
        logger = cls.get_logger()
        msg = f"Case {case_id}: {action}"
        if details:
            msg += f" - {details}"
        logger.info(msg)
    
    @classmethod
    def log_error(cls, error_msg, exception=None):
        """Log error with optional exception"""
        logger = cls.get_logger()
        if exception:
            logger.error(f"{error_msg}: {str(exception)}", exc_info=True)
        else:
            logger.error(error_msg)


# Convenience function
def get_logger(name='forenstiq'):
    """Get logger instance"""
    return ForenstiqLogger.get_logger(name)