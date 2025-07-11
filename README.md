# Discord OpenAI Bot

A scalable Discord bot using Python, Discord.py, and OpenAI.

## Features
- Modular structure for easy feature expansion
- OpenAI integration for intelligent, persona-driven responses
- Simple command handler (e.g., `!ping`, `!ask`, `!opinion`, `!who_won`)

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
- `src/` - Main source code (commands, configuration, OpenAI integration)
- `tests/` - Unit tests

## Adding Features
Add new commands or cogs in the `src/` directory for extensibility.

## Notes
- The `.env` file is gitignored for security.
- See `src/bot.py` for example commands and persona prompts.
