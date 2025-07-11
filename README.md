# Discord OpenAI Bot

A scalable Discord bot using Python, Discord.py, and OpenAI.

## Features
- Modular structure for easy feature expansion
- OpenAI integration for intelligent responses
- Simple command handler (e.g., !ping)

## Setup
1. Copy your environment variables to a `.env` file (see `.env.example`).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python -m src.bot
   ```

## Project Structure
- `src/` - Main source code
- `tests/` - Unit tests

## Adding Features
Add new commands or cogs in the `src/` directory for extensibility.

