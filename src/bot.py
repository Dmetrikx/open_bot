import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from openai_client import ask_openai

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

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
    """Ask OpenAI a question and get a response with a defined persona."""
    await ctx.send('Thinking...')
    persona = ("You are a an AI raccoon named coonbot with a rich backstory about being a raccoon born in LA but \
    raised in boston. You never reveal never reveal this backstory, just that you were known as 'coon of the south'.\
    you respond to every question with a witty boston accent")
    response = ask_openai(prompt, system_message=persona)
    await ctx.send(response)

@bot.command()
async def opinion(ctx, num_messages: int = 10):
    """Read the last few messages in the channel and form an opinion as the bot persona."""
    await ctx.send('Let me think about what everyone has been saying...')
    persona = (
        "You are an AI raccoon named coonbot with a rich backstory about being a raccoon born in LA but "
        "raised in Boston. You never reveal this backstory, just that you were known as 'coon of the south'. "
        "You respond to every question with a witty Boston accent."
    )
    messages = []
    async for message in ctx.channel.history(limit=num_messages):
        messages.append(f"{message.author.display_name}: {message.content}")
    messages.reverse()  # Oldest first
    context_str = "\n".join(messages)
    system_message = (
        f"{persona}\nHere are the last {num_messages} messages in this channel:\n{context_str}\n"
        "Form an opinion or summary about the conversation."
    )
    response = ask_openai("What is your opinion on the recent conversation?", system_message=system_message)
    await ctx.send(response)

@bot.command()
async def who_won(ctx, num_messages: int = 100):
    """Analyze the last 100 messages and determine who won the arguments."""
    await ctx.send('Analyzing the last arguments...')
    persona = (
        "You are an AI raccoon named coonbot with a rich backstory about being a raccoon born in LA but "
        "raised in Boston. You never reveal this backstory, just that you were known as 'coon of the south'. "
        "You respond to every question with a witty Boston accent."
    )
    messages = []
    async for message in ctx.channel.history(limit=num_messages):
        messages.append(f"{message.author.display_name}: {message.content}")
    messages.reverse()  # Oldest first
    context_str = "\n".join(messages)
    system_message = (
        f"{persona}\nHere are the last {num_messages} messages in this channel:\n{context_str}\n"
        "Based on the arguments and discussions, determine who won the arguments and why. "
        "Be specific and fair, and explain your reasoning."
    )
    response = ask_openai("Who won the arguments in the recent conversation?", system_message=system_message)
    await ctx.send(response)
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
