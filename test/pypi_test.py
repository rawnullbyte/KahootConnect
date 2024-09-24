from KahootConnect import KahootClient
import asyncio
import logging

# Set up a custom logger (optional)
def setup_logger():
    custom_logger = logging.getLogger('kahoot')
    custom_logger.setLevel(logging.INFO)
    
    # Create a console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Add the handler to the logger
    custom_logger.addHandler(ch)
    
    return custom_logger

async def join_kahoot():
    # Optionally pass a custom logger; otherwise, logging will be silent by default
    logger = setup_logger()

    # Create an instance of KahootClient with the logger
    client = KahootClient(logger=logger)
    
    # Call the join method with the game pin and nickname
    await client.join(6330297, "Pybot925531823")

# Run the event loop
asyncio.run(join_kahoot())
