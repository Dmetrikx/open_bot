import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from client import ask, image_opinion_openai
import asyncio
from personas import OPEN_AI_PERSONA as PERSONA

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

def format_channel_history(ctx, num_messages):
    messages = []
    async def fetch():
        async for message in ctx.channel.history(limit=num_messages):
            messages.append(f"{message.author.display_name}: {message.content}")
        messages.reverse()
        return "\n".join(messages)
    return fetch

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def ping(ctx):
    """A simple ping command."""
    await ctx.send('Pong!')

@bot.command()
async def ask(ctx, *, prompt: str):
    """Ask OpenAI or Grok a question and get a response with a defined persona."""
    await ctx.send('Thinking...')
    provider = "openai"
    prompt_words = prompt.split()
    if prompt_words and prompt_words[0].lower() in ["grok", "openai"]:
        provider = prompt_words[0].lower()
        prompt = " ".join(prompt_words[1:])
    response = await asyncio.to_thread(ask, prompt, system_message=PERSONA, model="gpt-3.5-turbo-0125", provider=provider)
    # Send response in 2000-character pieces
    for i in range(0, len(response), 2000):
        await ctx.send(response[i:i+2000])

@bot.command()
async def opinion(ctx, num_messages: int = 10):
    """Read the last few messages in the channel and form an opinion as the bot persona."""
    await ctx.send('Let me think about what everyone has been saying...')
    context_str = await format_channel_history(ctx, num_messages)()
    system_message = (
        f"{PERSONA}\nHere are the last {num_messages} messages in this channel:\n{context_str}\n"
        "Form an opinion or summary about the conversation."
    )
    provider = "openai"
    # Check for provider override in command
    if ctx.message.content.split()[1:2] and ctx.message.content.split()[1].lower() in ["grok", "openai"]:
        provider = ctx.message.content.split()[1].lower()
    response = await asyncio.to_thread(ask, "What is your opinion on the recent conversation?", system_message=system_message, model="gpt-3.5-turbo-0125", provider=provider)
    for i in range(0, len(response), 2000):
        await ctx.send(response[i:i+2000])

@bot.command()
async def who_won(ctx, num_messages: int = 100):
    """Analyze the last 100 messages and determine who won the arguments."""
    await ctx.send('Analyzing the last arguments...')
    context_str = await format_channel_history(ctx, num_messages)()
    system_message = (
        f"{PERSONA}\nHere are the last {num_messages} messages in this channel:\n{context_str}\n"
        "Based on the arguments and discussions, determine who won the arguments and why. "
        "Be specific and fair, and explain your reasoning."
    )
    provider = "openai"
    if ctx.message.content.split()[1:2] and ctx.message.content.split()[1].lower() in ["grok", "openai"]:
        provider = ctx.message.content.split()[1].lower()
    response = ask("Who won the arguments in the recent conversation?", system_message=system_message, provider=provider)
    await ctx.send(response)

@bot.command()
async def user_opinion(ctx, member: discord.Member, days: int = 3, max_messages: int = 200):
    """Analyze all messages sent by a user over the last few days and form an opinion on that user."""
    await ctx.send(f'Analyzing {member.display_name}...')
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    after = now - timedelta(days=days)
    messages = []
    async for message in ctx.channel.history(limit=max_messages, after=after):
        if message.author.id == member.id:
            messages.append(f"{message.author.display_name}: {message.content}")
    if not messages:
        await ctx.send(f"No messages found for {member.display_name} in the last {days} days.")
        return
    context_str = "\n".join(messages)
    system_message = (
        f"Here are all the messages sent by {member.display_name} in the last {days} days in this channel:\n{context_str}\n"
    )
    provider = "openai"
    if ctx.message.content.split()[2:3] and ctx.message.content.split()[2].lower() in ["grok", "openai"]:
        provider = ctx.message.content.split()[2].lower()
    response = ask(f"What is your opinion of {member.display_name}?", system_message=system_message, provider=provider)
    await ctx.send(response)

@bot.command()
async def most(ctx, *, question: str):
    """Generalized command to ask who is the most X or most likely to do Y in the chat. Handles both a single word or a sentence."""
    num_messages = 100
    await ctx.send(f"Analyzing: {question} (last {num_messages} messages)...")
    provider = "openai"
    question_words = question.split()
    if question_words and question_words[0].lower() in ["grok", "openai"]:
        provider = question_words[0].lower()
        question = " ".join(question_words[1:])
    messages = []
    user_message_count = {}
    async for message in ctx.channel.history(limit=num_messages):
        if message.author.bot:
            continue
        messages.append(f"{message.author.display_name}: {message.content}")
        user_message_count[message.author.display_name] = user_message_count.get(message.author.display_name, 0) + 1
    # Get the most active users (top 5)
    active_users = sorted(user_message_count.items(), key=lambda x: x[1], reverse=True)[:5]
    active_user_names = [user for user, _ in active_users]
    context_str = "\n".join(messages)
    # Detect if question is a single word or a sentence
    if len(question.split()) == 1:
        prompt = f"Who is the most {question} in the recent conversation?"
    else:
        prompt = question
    system_message = (
        f"{PERSONA}\nHere are the last {num_messages} messages in this channel:\n{context_str}\n"
        f"Among the most active users ({', '.join(active_user_names)}), answer the following question: {question}. "
        f"Explain your reasoning as Coonbot."
    )
    response = ask(prompt, system_message=system_message, provider=provider)
    await ctx.send(response)
@bot.command()
async def image_opinion(ctx):
    """Form an opinion on an image (attachment, URL, or reply to an image). Optionally provide a custom prompt. Use 'grok' to analyze with Grok."""
    image_url = None
    custom_prompt = None
    provider = "openai"
    content_args = ctx.message.content.split()

    # Check for provider keyword
    if len(content_args) > 1 and content_args[1].lower() == "grok":
        provider = "grok"
        # Shift arguments so image URL or prompt comes after 'grok'
        content_args = [content_args[0]] + content_args[2:]

    # Check for attachment first
    if ctx.message.attachments:
        image_url = ctx.message.attachments[0].url
        if len(content_args) > 1:
            custom_prompt = " ".join(content_args[1:])
    # If replying to a message with an image
    elif ctx.message.reference:
        try:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if replied_msg.attachments:
                image_url = replied_msg.attachments[0].url
            if len(content_args) > 1:
                custom_prompt = " ".join(content_args[1:])
        except Exception as e:
            await ctx.send(f"Could not fetch replied message: {e}")
            return
    # If no attachment or reply, check for image URL in message content
    elif len(content_args) > 1:
        possible_url = content_args[1]
        if possible_url.startswith("http://") or possible_url.startswith("https://"):
            image_url = possible_url
            if len(content_args) > 2:
                custom_prompt = " ".join(content_args[2:])
        else:
            custom_prompt = " ".join(content_args[1:])
    if not image_url:
        await ctx.send("Please attach an image, provide a valid image URL (starting with http/https), or reply to a message with an image.")
        return
    await ctx.send("Analyzing image, one sec...")
    try:
        if provider == "grok":
            from client import image_opinion_grok
            opinion = image_opinion_grok(image_url, system_message=PERSONA, custom_prompt=custom_prompt)
        else:
            opinion = image_opinion_openai(image_url, system_message=PERSONA, custom_prompt=custom_prompt)
        await ctx.send(opinion)
    except Exception as e:
        await ctx.send(f"Error analyzing image: {e}")
# Add more commands or cogs here for extensibility
@bot.command()
@commands.is_owner()
async def clear_commands(ctx):
    """Clear all global slash commands from Discord."""
    bot.tree.clear_commands(guild=None)  # Remove await here
    await bot.tree.sync()
    await ctx.send("Cleared all global slash commands.")

def main():
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
