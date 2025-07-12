"""
Enhanced Error Handling Utilities for SEO Audit Tool

Provides robust error handling, logging, and recovery mechanisms for field use.
"""

import functools
import logging
import traceback
import time
import requests
from typing import Any, Callable, Optional, Dict, Union

class AuditError(Exception):
    """Base exception for SEO audit operations"""
    pass

class CrawlingError(AuditError):
    """Exception raised during website crawling"""
    pass

class AnalysisError(AuditError):
    """Exception raised during SEO analysis"""
    pass

class ReportingError(AuditError):
    """Exception raised during report generation"""
    pass

class ErrorHandler:
    """Enhanced error handling with retry logic and graceful degradation"""
    
    def __init__(self, logger_name='seo_audit_errors'):
        self.logger = self._setup_logger(logger_name)
        self.error_counts = {}
        
    def _setup_logger(self, name):
        """Setup enhanced logging"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # File handler for errors
            file_handler = logging.FileHandler('seo_audit_errors.log')
            file_handler.setLevel(logging.ERROR)
            
            # Console handler for warnings and errors
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            
            # Detailed formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
        return logger
        
    def with_retry(self, max_retries=3, delay=1, exponential_backoff=True, 
                   exceptions=(Exception,), fallback=None):
        """
        Decorator for adding retry logic to functions
        
        Args:
            max_retries: Maximum number of retry attempts
            delay: Initial delay between retries (seconds)
            exponential_backoff: Whether to use exponential backoff
            exceptions: Tuple of exceptions to catch and retry
            fallback: Fallback value to return if all retries fail
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                current_delay = delay
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        # Log the attempt
                        if attempt < max_retries:
                            self.logger.warning(
                                f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}"
                            )
                            time.sleep(current_delay)
                            
                            if exponential_backoff:
                                current_delay *= 2
                        else:
                            # Final attempt failed
                            self.logger.error(
                                f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                            )
                            self._record_error(func.__name__, e)
                            
                # Return fallback or raise final exception
                if fallback is not None:
                    self.logger.info(f"Using fallback value for {func.__name__}")
                    return fallback
                else:
                    raise last_exception
                    
            return wrapper
        return decorator
        
    def safe_execute(self, func: Callable, *args, fallback=None, 
                    error_message="Operation failed", **kwargs):
        """
        Safely execute a function with error handling
        
        Args:
            func: Function to execute
            *args: Arguments for the function
            fallback: Fallback value if function fails
            error_message: Custom error message
            **kwargs: Keyword arguments for the function
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"{error_message}: {str(e)}")
            self.logger.debug(traceback.format_exc())
            self._record_error(func.__name__, e)
            
            if fallback is not None:
                return fallback
            raise
            
    def handle_network_errors(self, url: str, timeout: int = 30):
        """
        Decorator for handling network-related errors
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.Timeout:
                    self.logger.error(f"Timeout error for {url} (timeout: {timeout}s)")
                    raise CrawlingError(f"Request timeout for {url}")
                except requests.exceptions.ConnectionError:
                    self.logger.error(f"Connection error for {url}")
                    raise CrawlingError(f"Cannot connect to {url}")
                except requests.exceptions.HTTPError as e:
                    self.logger.error(f"HTTP error for {url}: {e.response.status_code}")
                    raise CrawlingError(f"HTTP {e.response.status_code} error for {url}")
                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Request error for {url}: {str(e)}")
                    raise CrawlingError(f"Request failed for {url}: {str(e)}")
                    
            return wrapper
        return decorator
        
    def validate_data(self, data: Any, required_fields: list = None, 
                     data_type: type = None, min_length: int = None):
        """
        Validate data with comprehensive checks
        
        Args:
            data: Data to validate
            required_fields: Required fields for dict data
            data_type: Expected data type
            min_length: Minimum length for sequences
        """
        if data is None:
            raise ValueError("Data cannot be None")
            
        if data_type and not isinstance(data, data_type):
            raise TypeError(f"Expected {data_type.__name__}, got {type(data).__name__}")
            
        if min_length and hasattr(data, '__len__') and len(data) < min_length:
            raise ValueError(f"Data length {len(data)} is less than minimum {min_length}")
            
        if required_fields and isinstance(data, dict):
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
                
        return True
        
    def graceful_degradation(self, operation_name: str, critical: bool = False):
        """
        Decorator for graceful degradation of non-critical operations
        
        Args:
            operation_name: Name of the operation for logging
            critical: Whether failure should stop the entire process
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    self.logger.info(f"Successfully completed {operation_name}")
                    return result
                except Exception as e:
                    self.logger.warning(f"Failed {operation_name}: {str(e)}")
                    self._record_error(operation_name, e)
                    
                    if critical:
                        self.logger.error(f"Critical operation {operation_name} failed")
                        raise
                    else:
                        self.logger.info(f"Continuing without {operation_name} (non-critical)")
                        return None
                        
            return wrapper
        return decorator
        
    def _record_error(self, operation: str, error: Exception):
        """Record error statistics"""
        error_type = type(error).__name__
        key = f"{operation}:{error_type}"
        
        if key not in self.error_counts:
            self.error_counts[key] = 0
        self.error_counts[key] += 1
        
    def get_error_summary(self) -> Dict[str, int]:
        """Get summary of all recorded errors"""
        return self.error_counts.copy()
        
    def reset_error_counts(self):
        """Reset error counters"""
        self.error_counts.clear()

# Global error handler instance
error_handler = ErrorHandler()

# Convenience decorators
def retry_on_failure(max_retries=3, delay=1, exceptions=(Exception,)):
    """Simplified retry decorator"""
    return error_handler.with_retry(max_retries, delay, True, exceptions)

def handle_gracefully(operation_name: str, critical: bool = False):
    """Simplified graceful degradation decorator"""
    return error_handler.graceful_degradation(operation_name, critical)

def safe_network_request(url: str, timeout: int = 30):
    """Simplified network error handling decorator"""
    return error_handler.handle_network_errors(url, timeout)

def validate_input(required_fields: list = None, data_type: type = None, min_length: int = None):
    """Input validation decorator"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Validate first argument (usually the data)
            if args:
                error_handler.validate_data(args[0], required_fields, data_type, min_length)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Example usage patterns for field testing
class FieldTestingMixin:
    """Mixin to add field testing capabilities to audit components"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_handler = error_handler
        
    @handle_gracefully("chart_generation", critical=False)
    def safe_generate_chart(self, chart_type: str, data: dict):
        """Generate chart with error handling"""
        # Implementation would go here
        pass
        
    @retry_on_failure(max_retries=3, exceptions=(requests.RequestException,))
    @safe_network_request("", timeout=30)
    def robust_fetch_page(self, url: str):
        """Fetch page with retry and network error handling"""
        # Implementation would go here
        pass
        
    @validate_input(required_fields=['url', 'title'], data_type=dict)
    def process_page_data(self, page_data: dict):
        """Process page data with validation"""
        # Implementation would go here
        pass