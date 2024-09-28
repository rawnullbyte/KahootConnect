# About
KahootConnect is a Kahoot API written in python, that Kahoot can't take down 🤡 #REForever

# Installation

`pip install -U KahootConnect`
or, clone the repo and
`python3 -m pip install -e ./KahootConnect`

# Usage

**Join room**
```python
import asyncio
import logging
from kahoot_connect import KahootClient  # Assuming kahoot_connect is the module name where KahootClient is defined

# Configure logging
logging.basicConfig(level=logging.DEBUG)

async def main():
    # Create an instance of KahootClient
    client = KahootClient()

    # Define the game pin and nickname
    game_pin = "123456"  # Replace with the actual game PIN
    nickname = "Player1"  # Replace with the desired nickname

    try:
        # Join the Kahoot game
        await client.join(game_pin, nickname)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
```

# Documentation:
Work In Progress!

# Kahoot Docs
**(DOCS)**
 [Need api docs?](KahootProtocol.md)

**(OUTDATED DOCS)**
 [Need api docs?](KahootProtocolOutdated.md)
 [More detailed docs?](KahootProtocolDetailedOutdated.md)
