import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from client import ask_client, image_opinion_openai
import asyncio
from personas import OPEN_AI_PERSONA as PERSONA
from constants import DEFAULT_OPENAI_MODEL

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
    """Check if the bot is responsive."""
    await ctx.send('Pong!')

def extract_provider_and_args(args, default_provider="openai"):
    """Helper to extract provider and remaining args from a list of arguments."""
    provider = default_provider
    if args and args[0].lower() in ["grok", "openai"]:
        provider = args[0].lower()
        args = args[1:]
    return provider, args

async def send_long_response(ctx, response):
    """Helper to send long responses in 2000-char chunks."""
    for i in range(0, len(response), 2000):
        await ctx.send(response[i:i+2000])

@bot.command()
async def ask(ctx, *, prompt: str):
    """Ask a question to the bot persona. Usage: !ask [grok|openai] question"""
    await ctx.send('Thinking...')
    args = prompt.split()
    provider, args = extract_provider_and_args(args)
    prompt_text = " ".join(args) if args else prompt
    response = await asyncio.to_thread(
        ask_client, prompt_text, system_message=PERSONA, model=DEFAULT_OPENAI_MODEL, provider=provider
    )
    await send_long_response(ctx, response)

@bot.command()
async def opinion(ctx, *, arg: str = ""):
    """Summarize or form an opinion on recent messages. Usage: !opinion [grok|openai] [num_messages]"""
    await ctx.send('Let me think about what everyone has been saying...')
    args = arg.split()
    provider, args = extract_provider_and_args(args)
    num_messages = 10
    if args and args[0].isdigit():
        num_messages = int(args[0])
    context_str = await format_channel_history(ctx, num_messages)()
    system_message = (
        f"{PERSONA}\nHere are the last {num_messages} messages in this channel:\n{context_str}\n"
        "Form an opinion or summary about the conversation."
    )
    response = await asyncio.to_thread(
        ask_client, "What is your opinion on the recent conversation?", system_message=system_message,
        model=DEFAULT_OPENAI_MODEL, provider=provider
    )
    await send_long_response(ctx, response)

@bot.command()
async def who_won(ctx, *, arg: str = ""):
    """Analyze arguments and determine who won. Usage: !who_won [grok|openai] [num_messages]"""
    await ctx.send('Analyzing the last arguments...')
    args = arg.split()
    provider, args = extract_provider_and_args(args)
    num_messages = 100
    if args and args[0].isdigit():
        num_messages = int(args[0])
    context_str = await format_channel_history(ctx, num_messages)()
    system_message = (
        f"{PERSONA}\nHere are the last {num_messages} messages in this channel:\n{context_str}\n"
        "Based on the arguments and discussions, determine who won the arguments and why. "
        "Be specific and fair, and explain your reasoning."
    )
    response = await asyncio.to_thread(
        ask_client, "Who won the arguments in the recent conversation?", system_message=system_message,
        model=DEFAULT_OPENAI_MODEL, provider=provider
    )
    await send_long_response(ctx, response)

@bot.command()
async def user_opinion(ctx, member: discord.Member, *, arg: str = ""):
    """Form an opinion on a user. Usage: !user_opinion @user [grok|openai] [days] [max_messages]"""
    await ctx.send(f'Analyzing {member.display_name}...')
    from datetime import datetime, timedelta, timezone
    args = arg.split()
    provider, args = extract_provider_and_args(args)
    days = 3
    max_messages = 200
    if args and args[0].isdigit():
        days = int(args[0])
        args = args[1:]
    if args and args[0].isdigit():
        max_messages = int(args[0])
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
    response = await asyncio.to_thread(
        ask_client, f"What is your opinion of {member.display_name}?", system_message=system_message,
        model=DEFAULT_OPENAI_MODEL, provider=provider
    )
    await send_long_response(ctx, response)

@bot.command()
async def most(ctx, *, question: str):
    """Ask who is the most X or most likely to do Y. Usage: !most [grok|openai] question"""
    num_messages = 100
    await ctx.send(f"Analyzing: {question} (last {num_messages} messages)...")
    args = question.split()
    provider, args = extract_provider_and_args(args)
    question_text = " ".join(args) if args else question
    messages = []
    user_message_count = {}
    async for message in ctx.channel.history(limit=num_messages):
        if message.author.bot:
            continue
        messages.append(f"{message.author.display_name}: {message.content}")
        user_message_count[message.author.display_name] = user_message_count.get(message.author.display_name, 0) + 1
    active_users = sorted(user_message_count.items(), key=lambda x: x[1], reverse=True)[:5]
    active_user_names = [user for user, _ in active_users]
    context_str = "\n".join(messages)
    if len(question_text.split()) == 1:
        prompt = f"Who is the most {question_text} in the recent conversation?"
    else:
        prompt = question_text
    system_message = (
        f"{PERSONA}\nHere are the last {num_messages} messages in this channel:\n{context_str}\n"
        f"Among the most active users ({', '.join(active_user_names)}), answer the following question: {question_text}. "
        f"Explain your reasoning as Coonbot."
    )
    response = await asyncio.to_thread(
        ask_client, prompt, system_message=system_message, model=DEFAULT_OPENAI_MODEL, provider=provider
    )
    await send_long_response(ctx, response)

@bot.command()
async def image_opinion(ctx, *, arg: str = ""):
    """Form an opinion on an image. Usage: !image_opinion [grok|openai] [image_url|prompt]"""
    image_url = None
    custom_prompt = None
    args = arg.split()
    provider, args = extract_provider_and_args(args)
    content_args = ctx.message.content.split()
    # Check for attachment first
    if ctx.message.attachments:
        image_url = ctx.message.attachments[0].url
        if args:
            custom_prompt = " ".join(args)
    # If replying to a message with an image
    elif ctx.message.reference:
        try:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if replied_msg.attachments:
                image_url = replied_msg.attachments[0].url
            if args:
                custom_prompt = " ".join(args)
        except Exception as e:
            await ctx.send(f"Could not fetch replied message: {e}")
            return
    # If no attachment or reply, check for image URL in args
    elif args:
        possible_url = args[0]
        if possible_url.startswith("http://") or possible_url.startswith("https://"):
            image_url = possible_url
            if len(args) > 1:
                custom_prompt = " ".join(args[1:])
        else:
            custom_prompt = " ".join(args)
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
        await send_long_response(ctx, opinion)
    except Exception as e:
        await ctx.send(f"Error analyzing image: {e}")

@bot.command()
@commands.is_owner()
async def clear_commands(ctx):
    """Clear all global slash commands from Discord."""
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()
    await ctx.send("Cleared all global slash commands.")

@bot.command()
async def roast(ctx, member: discord.Member = None):
    """Roast a user. Usage: !roast @user or !roast as a reply to a message."""
    target_name = None
    roast_message = None
    # If user is mentioned
    if member:
        target_name = member.display_name
        system_message = f"{PERSONA}\nRoast {target_name} as if you were a boston comedian who grew up in the bronx. Dont be afraid to attack sexuality, its a joke and everyone gets it. Be really really mean."
        prompt = f"Roast {target_name}."
    # If command is a reply to a message
    elif ctx.message.reference:
        try:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            target_name = replied_msg.author.display_name
            roast_message = replied_msg.content
            system_message = f"{PERSONA}\nRoast {target_name} based on this message: '{roast_message}'. Be a boston comedian from the bronx, don't be afraid to attack sexuality, it's a joke and everyone gets it."
            prompt = f"Roast {target_name} for saying: {roast_message}"
        except Exception as e:
            await ctx.send(f"Could not fetch replied message: {e}")
            return
    else:
        await ctx.send("Please mention a user or reply to a message to roast.")
        return
    await ctx.send(f"Cooking up a roast for {target_name}...")
    response = await asyncio.to_thread(
        ask_client, prompt, system_message=system_message, model=DEFAULT_OPENAI_MODEL, provider="openai"
    )
    await send_long_response(ctx, response)

def main():
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
