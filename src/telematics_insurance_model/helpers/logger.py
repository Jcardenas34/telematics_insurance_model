import logging

'''
This module will set a global instance of the Redis client.
'''

# Will be gloabally accessible
logger: logging.Logger | None = None

def initialize_logger():
    """
    Establishes the connection to the Redis server and configures 
    the client instance for application-wide use.
    """
    global logger
    if logger is None:
        print("Creating Log ...")
        # A connection pool is integral for managing connections efficiently.
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)
        print("Log created")

    return logger
