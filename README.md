# Discord PinBoard Bot

A lightweight, professional Discord bot designed to archive your favorite community moments. When a user reacts with 📌, the bot captures the message and images then posts them to a dedicated archive channel.

---

## Features

*   **Full Media Support**: Automatically detects and embeds images, GIFs (Tenor/Giphy), and file attachments.
*   **Persistent Storage**: Saves pin counts and message history to JSON files (`pins.json`, `pinCount.json`) so data survives bot restarts.
*   **Smart Logging**: Colorful console output using `colorama` for easy real-time monitoring.
*   **Self-Cleaning UI**: Confirmation messages automatically delete after 10 seconds to keep your main chat clutter-free.
*   **Easy Configuration**: Use the `/setchannel` slash command to designate the pinboard destination.

---

## Setup & Installation

### 1. Prerequisites
*   Python 3.8 or higher
*   Discord Bot Token (with `Message Content` and `Server Members` intents enabled)

### 2. Install Dependencies
Run the following command to install the required libraries:

```bash
pip install discord.py python-dotenv colorama
```
