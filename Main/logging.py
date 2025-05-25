import logging

# Configure the root logger with desired settings.
logging.basicConfig(
    level=logging.INFO,  # Set the minimum logging level to INFO. Messages below this level will be ignored.
    
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",  # Define the log message format.
    
    datefmt="%d-%b-%y %H:%M:%S",  # Define the format for the timestamp in the log messages.
    
    handlers=[
        logging.FileHandler("log.txt"),  # Log messages will be written to the 'log.txt' file.
        logging.StreamHandler(),  # Log messages will also be displayed in the console (standard output).
    ],
)

# Silence noisy loggers from external libraries to reduce clutter.
logging.getLogger("httpx").setLevel(logging.ERROR)  # Set httpx logger level to ERROR, suppressing INFO and WARNING messages.

logging.getLogger("pyrogram").setLevel(logging.ERROR)  # Set pyrogram logger level to ERROR, suppressing INFO and WARNING messages.


def LOGGER(name: str) -> logging.Logger:
    """
    Retrieves a logger instance with the specified name.

    Args:
        name (str): The name of the logger to retrieve. Typically set to the module name (__name__).

    Returns:
        logging.Logger: A logger instance with the given name.
    """
    return logging.getLogger(name)