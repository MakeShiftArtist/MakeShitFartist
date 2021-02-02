import os
import json
from discord.ext import commands
import discord
from definitions import Database, Datetime

file = "ifunnydiscord.sqlite"


def _prefix_callable(bot, message):
    guild = message.guild
    db = Database(file)

    if guild:
        select = f'SELECT Prefix FROM GuildPrefixes WHERE GuildID = {guild.id}'
        _db_prefix = db.get_select(select)
        if _db_prefix is None:
            db.close()
            return '-'
        else:
            db.close()
            return str(_db_prefix)
    else:
        db.close()
        return '-'


async def get_prefix(bot, message):
    extras = _prefix_callable(bot, message)
    return commands.when_mentioned_or(extras)(bot, message)

intents = discord.Intents.all()
allowed_mentions = discord.AllowedMentions(everyone=False)
client = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    intents=intents,
    allowed_mentions=allowed_mentions
    )
client.remove_command('help')


@client.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@load.error
async def load_error(ctx, error):
    return


@client.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@unload.error
async def unload_error(ctx, error):
    return


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_ready():
    print(Datetime.get_full_date())
    print(f'Bot signed in as {client.user}')
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Game("@MakeShitFartist help")
    )
    db = Database(file)
    db.start()
    db.close()


@client.command(hidden=True)
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("Logging off...")
    await ctx.bot.logout()


@shutdown.error
async def shutdown_error(ctx, error):
    return


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.NotOwner):
        return
    elif isinstance(error, discord.Forbidden):
        return
    elif isinstance(error, commands.BadArgument):
        return await ctx.send(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send(error)
    elif isinstance(error, commands.MissingPermissions):
        return await ctx.send(error)
    elif isinstance(error, commands.BotMissingPermissions):
        return await ctx.send(error)
    elif isinstance(error, commands.CommandOnCooldown):
        time = round(error.retry_after*100)/100
        return await ctx.send(f"Command on cooldown. Try again in {time} seconds")
    else:
        await ctx.send(error)
        raise error


with open("tokens.json") as f:
    data = json.load(f)
    client.run(data["discord"])
