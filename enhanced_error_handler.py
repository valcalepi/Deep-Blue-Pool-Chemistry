"""
Enhanced Error Handler for Deep Blue Pool Chemistry.

This module provides enhanced error handling utilities for the application,
including decorators for GUI and CLI functions.
"""

import logging
import functools
import traceback
import sys

# Set up logger
logger = logging.getLogger(__name__)

def handle_gui_error(func):
    """
    Decorator for handling errors in GUI functions.
    
    This decorator catches exceptions, logs them, and shows an error message to the user.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            logger.debug(traceback.format_exc())
            
            # Show error message to user if we have access to messagebox
            try:
                import tkinter.messagebox as messagebox
                messagebox.showerror(
                    "Error",
                    f"An error occurred: {str(e)}\n\nPlease check the log file for details."
                )
            except ImportError:
                # If messagebox is not available, just log the error
                pass
                
            return None
    return wrapper

def handle_cli_error(func):
    """
    Decorator for handling errors in CLI functions.
    
    This decorator catches exceptions, logs them, and prints an error message to the console.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            logger.debug(traceback.format_exc())
            
            # Print error message to console
            print(f"Error: {str(e)}")
            print("Please check the log file for details.")
                
            return None
    return wrapper

def handle_critical_error(func):
    """
    Decorator for handling critical errors that should terminate the application.
    
    This decorator catches exceptions, logs them, shows an error message, and exits the application.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.critical(f"Critical error in {func.__name__}: {e}")
            logger.critical(traceback.format_exc())
            
            # Try to show GUI error if possible
            try:
                import tkinter.messagebox as messagebox
                messagebox.showerror(
                    "Critical Error",
                    f"A critical error has occurred: {str(e)}\n\n"
                    "The application will now exit.\n\n"
                    "Please check the log file for details."
                )
            except ImportError:
                # Fall back to console error
                print(f"Critical Error: {str(e)}")
                print("The application will now exit.")
                print("Please check the log file for details.")
                
            sys.exit(1)
    return wrapper

class ErrorHandler:
    """
    Class-based error handler for use in contexts where decorators are not suitable.
    
    This class provides methods for handling errors in different contexts.
    """
    
    @staticmethod
    def handle_gui_context(error_message, exception, show_dialog=True):
        """
        Handle errors in GUI contexts.
        
        Args:
            error_message: A descriptive error message
            exception: The exception that was raised
            show_dialog: Whether to show a dialog to the user
            
        Returns:
            None
        """
        logger.error(f"{error_message}: {exception}")
        logger.debug(traceback.format_exc())
        
        if show_dialog:
            try:
                import tkinter.messagebox as messagebox
                messagebox.showerror(
                    "Error",
                    f"{error_message}: {str(exception)}\n\n"
                    "Please check the log file for details."
                )
            except ImportError:
                pass
    
    @staticmethod
    def handle_cli_context(error_message, exception, show_message=True):
        """
        Handle errors in CLI contexts.
        
        Args:
            error_message: A descriptive error message
            exception: The exception that was raised
            show_message: Whether to print a message to the console
            
        Returns:
            None
        """
        logger.error(f"{error_message}: {exception}")
        logger.debug(traceback.format_exc())
        
        if show_message:
            print(f"Error: {error_message}: {str(exception)}")
            print("Please check the log file for details.")