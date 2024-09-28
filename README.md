## Overview

`KahootClient` is a Python client for connecting to Kahoot games using WebSockets. This package allows users to join a Kahoot game and send messages to the game server.

## Features

- Connect to Kahoot game servers.
- Handle session management and token decoding.
- Send and receive messages from the game server.
- Customizable logging for debugging purposes.

# About
KahootConnect is a Kahoot API written in python, that Kahoot can't take down 🤡 #REForever

# Installation

```bash
pip install -U KahootConnect
```
or clone the repo and
```bash
python3 -m pip install -e ./KahootConnect
```

# Usage

### Importing the Package

First, you need to import the `KahootClient` class from the package:

```python
from kahoot_client import KahootClient
```

### Creating a Client Instance

You can create an instance of the `KahootClient` class with optional logging:

```python
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create a Kahoot client instance
client = KahootClient()
```

### Joining a Game

To join a Kahoot game, use the `join` method, passing the game pin and your nickname:

```python
import asyncio

async def main():
    game_pin = "123456"  # Replace with your game pin
    nickname = "YourNickname"  # Replace with your desired nickname
    await client.join(game_pin, nickname)

# Run the async function
asyncio.run(main())
```

# Kahoot Docs
**(DOCS)**
 [Need api docs?](KahootProtocol.md)

**(OUTDATED DOCS)**
 [Need api docs?](KahootProtocolOutdated.md)
 [More detailed docs?](KahootProtocolDetailedOutdated.md)

# Logging

The client uses Python's built-in logging module to provide debug information. You can configure the logging level to control the verbosity:

```
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG to see all logs
```

# Error Handling

The `join` method may raise exceptions, particularly related to WebSocket connections. It's recommended to wrap your calls in try-except blocks to handle potential errors gracefully.

```
try:
    await client.join(game_pin, nickname)
except Exception as e:
    print(f"An error occurred: {e}")
```

# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you find any bugs or have suggestions for improvements.

