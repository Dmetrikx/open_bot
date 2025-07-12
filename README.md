# Discord OpenAI Bot

A scalable Discord bot using Python, Discord.py, and OpenAI.

## Features
- Modular structure for easy feature expansion
- OpenAI integration for intelligent, persona-driven responses
- Simple command handler (e.g., `!ping`, `!ask`, `!opinion`, `!who_won`)

## Commands & Usage
Interact with the bot using the following commands in any Discord channel where the bot is present:

### `!ping`
Check if the bot is online.
- Example: `!ping`

### `!ask <question>`
Ask the bot any question and get a persona-driven response.
- Example: `!ask What do you think about Boston politics?`
- Example: `!ask Who would win in a fight, Batman or Superman?`

### `!opinion [num_messages]`
Get the bot's opinion or summary on the last few messages in the channel.
- Example: `!opinion` (default: 10 messages)
- Example: `!opinion 20` (analyzes last 20 messages)

### `!who_won [num_messages]`
Analyze recent arguments and determine who won.
- Example: `!who_won` (default: 100 messages)
- Example: `!who_won 50` (analyzes last 50 messages)

### `!user_opinion <@user> [days] [max_messages]`
Get the bot's opinion on a specific user based on their recent messages.
- Example: `!user_opinion @Alice` (default: 3 days, 200 messages)
- Example: `!user_opinion @Bob 5 100` (analyzes Bob's last 100 messages over 5 days)

### `!most <question>`
Ask who is the most X or most likely to do Y in the chat.
- Example: `!most helpful` (default: last 100 messages)
- Example: `!most Who is most likely to start an argument?`

### `!image_opinion <image_url> [custom_prompt]` / attach an image / reply to an image
Form an opinion on an image by:
- Attaching an image and typing `!image_opinion` (optionally add a custom prompt after the command)
- Providing an image URL: `!image_opinion https://example.com/image.jpg` (optionally add a custom prompt after the URL)
- Replying to a message with an image attachment and typing `!image_opinion` (optionally add a custom prompt after the command)

**Custom prompt usage examples:**
- `!image_opinion https://example.com/image.jpg What do you think of this meme?`
- *(attach an image)* `!image_opinion Give a funny take on this picture.`
- *(reply to an image)* `!image_opinion Be controversial about this photo.`

If no custom prompt is provided, the bot will use its default style.

### Provider Override (OpenAI/Grok)
You can override the AI provider for any command that uses language models by prefixing your prompt with `grok` or `openai`:
- Example: `!ask grok Who are you?` (uses Grok)
- Example: `!ask openai Who are you?` (uses OpenAI)
- Example: `!most grok Who is most likely to start an argument?`
- Example: `!opinion grok` (uses Grok for opinion)
- Example: `!who_won grok` (uses Grok for argument analysis)
- Example: `!user_opinion @Alice grok` (uses Grok for user analysis)

If no provider is specified, OpenAI is used by default.

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

### Setup for Grok
To use Grok, you must install `xai-sdk` and set the `XAI_API_KEY` environment variable. See requirements.txt for details.
