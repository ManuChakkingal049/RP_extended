"""
Logging Module
Provides structured logging capabilities with multiple handlers
"""

import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class AppLogger:
    """
    Application logger with structured logging support
    """
    
    _loggers = {}
    _log_dir = Path("logs")
    
    @classmethod
    def setup_logging(
        cls,
        log_level: str = "INFO",
        log_to_file: bool = True,
        log_to_console: bool = True,
        structured: bool = True
    ):
        """
        Setup application-wide logging configuration
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to log to file
            log_to_console: Whether to log to console
            structured: Whether to use structured logging (JSON format)
        """
        # Create logs directory
        if log_to_file:
            cls._log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove existing handlers
        root_logger.handlers = []
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            if structured:
                console_handler.setFormatter(StructuredFormatter())
            else:
                console_handler.setFormatter(StandardFormatter())
            
            root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if log_to_file:
            # Application log
            app_log_file = cls._log_dir / "app.log"
            file_handler = logging.handlers.RotatingFileHandler(
                app_log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            
            if structured:
                file_handler.setFormatter(StructuredFormatter())
            else:
                file_handler.setFormatter(StandardFormatter())
            
            root_logger.addHandler(file_handler)
            
            # Error log (errors only)
            error_log_file = cls._log_dir / "error.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(StructuredFormatter() if structured else StandardFormatter())
            root_logger.addHandler(error_handler)
            
            # Audit log (for security and compliance)
            audit_log_file = cls._log_dir / "audit.log"
            audit_handler = logging.handlers.RotatingFileHandler(
                audit_log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=10  # Keep more audit logs
            )
            audit_handler.setLevel(logging.INFO)
            audit_handler.setFormatter(StructuredFormatter())
            
            # Create audit logger
            audit_logger = logging.getLogger('audit')
            audit_logger.addHandler(audit_handler)
            audit_logger.setLevel(logging.INFO)
            audit_logger.propagate = False  # Don't propagate to root logger
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance
        
        Args:
            name: Logger name (typically __name__)
            
        Returns:
            logging.Logger: Logger instance
        """
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @classmethod
    def get_audit_logger(cls) -> logging.Logger:
        """
        Get the audit logger
        
        Returns:
            logging.Logger: Audit logger instance
        """
        return logging.getLogger('audit')


class StructuredFormatter(logging.Formatter):
    """
    Formatter that outputs logs in structured JSON format
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON
        
        Args:
            record: Log record to format
            
        Returns:
            str: JSON formatted log entry
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'details'):
            log_data['details'] = record.details
        
        if hasattr(record, 'session_id'):
            log_data['session_id'] = record.session_id
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        return json.dumps(log_data)


class StandardFormatter(logging.Formatter):
    """
    Standard text formatter for logs
    """
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


class AuditLogger:
    """
    Specialized logger for audit trail
    """
    
    def __init__(self):
        self.logger = AppLogger.get_audit_logger()
    
    def log_action(
        self,
        action: str,
        session_id: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        status: str = "success"
    ):
        """
        Log an audit action
        
        Args:
            action: Action being performed
            session_id: Session ID
            details: Additional details
            user_id: User ID (if applicable)
            status: Action status (success, failure, warning)
        """
        audit_entry = {
            'action': action,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'status': status,
            'details': details or {}
        }
        
        if user_id:
            audit_entry['user_id'] = user_id
        
        self.logger.info(
            f"Audit: {action}",
            extra={'details': audit_entry}
        )
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        session_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log a security event
        
        Args:
            event_type: Type of security event
            severity: Severity (low, medium, high, critical)
            description: Event description
            session_id: Session ID (if applicable)
            details: Additional details
        """
        security_entry = {
            'event_type': event_type,
            'severity': severity,
            'description': description,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'details': details or {}
        }
        
        if session_id:
            security_entry['session_id'] = session_id
        
        # Log at appropriate level based on severity
        log_level = {
            'low': logging.INFO,
            'medium': logging.WARNING,
            'high': logging.ERROR,
            'critical': logging.CRITICAL
        }.get(severity.lower(), logging.WARNING)
        
        self.logger.log(
            log_level,
            f"Security Event: {event_type}",
            extra={'details': security_entry}
        )
    
    def log_data_access(
        self,
        data_type: str,
        action: str,
        session_id: str,
        record_count: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log data access events
        
        Args:
            data_type: Type of data accessed
            action: Action performed (read, write, delete)
            session_id: Session ID
            record_count: Number of records affected
            details: Additional details
        """
        access_entry = {
            'data_type': data_type,
            'action': action,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'details': details or {}
        }
        
        if record_count is not None:
            access_entry['record_count'] = record_count
        
        self.logger.info(
            f"Data Access: {data_type} - {action}",
            extra={'details': access_entry}
        )


# Initialize logging on module import
AppLogger.setup_logging()
