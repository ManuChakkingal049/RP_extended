"""
Security Module
Handles security features including file validation, session management, and input sanitization
"""

import hashlib
import secrets
import re
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Manages security features for the application
    """
    
    # Configuration
    MAX_FILE_SIZE_MB = 10
    ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
    SESSION_TIMEOUT_MINUTES = 60
    MAX_SESSIONS = 100
    
    # Dangerous patterns to check in file content
    DANGEROUS_PATTERNS = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'onerror=',
        r'onclick=',
        r'eval\(',
        r'exec\(',
        r'__import__',
    ]
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self._cleanup_old_sessions()
    
    def generate_session_id(self) -> str:
        """
        Generate a cryptographically secure session ID
        
        Returns:
            str: Unique session ID
        """
        session_id = secrets.token_hex(16)
        self.sessions[session_id] = {
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'actions': []
        }
        
        logger.info(f"New session created: {session_id[:8]}...")
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        """
        Validate if a session is still active
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            bool: True if valid and active
        """
        if session_id not in self.sessions:
            logger.warning(f"Invalid session ID: {session_id[:8]}...")
            return False
        
        session = self.sessions[session_id]
        last_activity = session['last_activity']
        
        # Check if session has timed out
        timeout = timedelta(minutes=self.SESSION_TIMEOUT_MINUTES)
        if datetime.now() - last_activity > timeout:
            logger.warning(f"Session timed out: {session_id[:8]}...")
            del self.sessions[session_id]
            return False
        
        # Update last activity
        session['last_activity'] = datetime.now()
        return True
    
    def _cleanup_old_sessions(self):
        """Remove old and expired sessions"""
        timeout = timedelta(minutes=self.SESSION_TIMEOUT_MINUTES)
        now = datetime.now()
        
        expired = [
            sid for sid, sess in self.sessions.items()
            if now - sess['last_activity'] > timeout
        ]
        
        for sid in expired:
            del self.sessions[sid]
            logger.info(f"Expired session removed: {sid[:8]}...")
        
        # Limit total sessions
        if len(self.sessions) > self.MAX_SESSIONS:
            # Remove oldest sessions
            sorted_sessions = sorted(
                self.sessions.items(),
                key=lambda x: x[1]['last_activity']
            )
            
            to_remove = sorted_sessions[:len(self.sessions) - self.MAX_SESSIONS]
            for sid, _ in to_remove:
                del self.sessions[sid]
                logger.info(f"Session removed (limit exceeded): {sid[:8]}...")
    
    def validate_file_upload(self, uploaded_file) -> bool:
        """
        Validate uploaded file for security
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            bool: True if file passes validation
        """
        try:
            # Check file extension
            file_ext = self._get_file_extension(uploaded_file.name)
            if file_ext not in self.ALLOWED_EXTENSIONS:
                logger.warning(f"Invalid file extension: {file_ext}")
                return False
            
            # Check file size
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if file_size_mb > self.MAX_FILE_SIZE_MB:
                logger.warning(f"File too large: {file_size_mb:.2f}MB")
                return False
            
            # Check for dangerous content patterns
            try:
                content = uploaded_file.read()
                uploaded_file.seek(0)  # Reset file pointer
                
                content_str = content.decode('utf-8', errors='ignore')
                
                for pattern in self.DANGEROUS_PATTERNS:
                    if re.search(pattern, content_str, re.IGNORECASE):
                        logger.warning(f"Dangerous pattern detected in file: {pattern}")
                        return False
                        
            except Exception as e:
                logger.error(f"Error scanning file content: {str(e)}")
                # If we can't read it, it's probably binary (Excel) - allow it
                pass
            
            logger.info(f"File validation passed: {uploaded_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            return False
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename"""
        parts = filename.lower().split('.')
        if len(parts) > 1:
            return '.' + parts[-1]
        return ''
    
    def sanitize_input(self, input_str: str, max_length: int = 1000) -> str:
        """
        Sanitize user input string
        
        Args:
            input_str: Input string to sanitize
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized string
        """
        if not input_str:
            return ""
        
        # Truncate to max length
        sanitized = input_str[:max_length]
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Remove multiple whitespaces
        sanitized = ' '.join(sanitized.split())
        
        return sanitized
    
    def validate_numeric_input(
        self,
        value: float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allow_negative: bool = False
    ) -> bool:
        """
        Validate numeric input
        
        Args:
            value: Numeric value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allow_negative: Whether negative values are allowed
            
        Returns:
            bool: True if valid
        """
        try:
            # Check if it's a valid number
            if not isinstance(value, (int, float)):
                return False
            
            # Check for NaN or infinity
            if np.isnan(value) or np.isinf(value):
                return False
            
            # Check negative
            if not allow_negative and value < 0:
                logger.warning(f"Negative value not allowed: {value}")
                return False
            
            # Check range
            if min_value is not None and value < min_value:
                logger.warning(f"Value below minimum: {value} < {min_value}")
                return False
            
            if max_value is not None and value > max_value:
                logger.warning(f"Value above maximum: {value} > {max_value}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Numeric validation error: {str(e)}")
            return False
    
    def hash_sensitive_data(self, data: str) -> str:
        """
        Create a hash of sensitive data for logging
        
        Args:
            data: Sensitive data to hash
            
        Returns:
            str: SHA256 hash of the data
        """
        return hashlib.sha256(data.encode()).hexdigest()
    
    def check_rate_limit(
        self,
        session_id: str,
        action: str,
        max_actions: int = 10,
        time_window_seconds: int = 60
    ) -> bool:
        """
        Check if an action is within rate limits
        
        Args:
            session_id: Session ID
            action: Action being performed
            max_actions: Maximum actions allowed in time window
            time_window_seconds: Time window in seconds
            
        Returns:
            bool: True if within limits
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Initialize action tracking if needed
        if 'rate_limits' not in session:
            session['rate_limits'] = {}
        
        if action not in session['rate_limits']:
            session['rate_limits'][action] = []
        
        # Clean old entries
        cutoff_time = datetime.now() - timedelta(seconds=time_window_seconds)
        session['rate_limits'][action] = [
            t for t in session['rate_limits'][action]
            if t > cutoff_time
        ]
        
        # Check limit
        if len(session['rate_limits'][action]) >= max_actions:
            logger.warning(
                f"Rate limit exceeded for action '{action}' "
                f"in session {session_id[:8]}..."
            )
            return False
        
        # Record action
        session['rate_limits'][action].append(datetime.now())
        return True
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get information about a session
        
        Args:
            session_id: Session ID
            
        Returns:
            Dict: Session information or None
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            'session_id': session_id,
            'created_at': session['created_at'].isoformat(),
            'last_activity': session['last_activity'].isoformat(),
            'duration_minutes': (
                datetime.now() - session['created_at']
            ).total_seconds() / 60,
            'actions_count': len(session.get('actions', []))
        }


# Import numpy for validation
import numpy as np
