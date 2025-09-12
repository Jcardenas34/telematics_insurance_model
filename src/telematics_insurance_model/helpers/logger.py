import os
import logging
from datetime import datetime 

# Will be gloabally accessible
logger: logging.Logger | None = None

def initialize_logger():
    """
    Creates a singleton instance of a logger.

    Returns:
        logging.Logger: Configured logger instance.
    Raises:
        Exception: If logger initialization fails.

    """
    # Ensure that the logs directory exists
    os.makedirs('logs', exist_ok=True)

    global logger
    if logger is None:
        print("Creating Log ...")
        
        # Create a timestamped log file
        now = str(datetime.now()).replace(" ","_")
        path = f"logs/telematics_data_{now}.log"

        logging.basicConfig(filename=path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)
        print(f"Log created: {path}")

    return logger


def initialize_training_logger(model_name: str):
    """
    Creates a singleton instance of a logger.

    Returns:
        logging.Logger: Configured logger instance.
    Raises:
        Exception: If logger initialization fails.

    """
    # Ensure that the logs directory exists
    os.makedirs('logs', exist_ok=True)

    global logger
    if logger is None:
        print("Creating Log ...")
        
        # Create a timestamped log file
        now = str(datetime.now()).replace(" ","_")
        path = f"logs/log_regessor_{model_name}_{now}.log"

        logging.basicConfig(filename=path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)
        print(f"Log created: {path}")

    return logger


def initialize_evaluation_logger(model_name: str):
    """
    Creates a singleton instance of a logger.

    Returns:
        logging.Logger: Configured logger instance.
    Raises:
        Exception: If logger initialization fails.

    """
    # Ensure that the logs directory exists
    os.makedirs('logs', exist_ok=True)

    global logger
    if logger is None:
        print("Creating Log ...")
        
        # Create a timestamped log file
        now = str(datetime.now()).replace(" ","_")
        path = f"logs/log_regessor_eval_{model_name}_{now}.log"

        logging.basicConfig(filename=path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)
        print(f"Log created: {path}")

    return logger