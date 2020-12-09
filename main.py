import os
from discord.ext import commands
import discord
from definitions import Database

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
    command_prefix=get_prefix, case_insensitive=True,
    intents=intents, allowed_mentions=allowed_mentions
    )
client.remove_command('help')


@client.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@load.error
async def load_error(ctx, error):
    return

"""
@client.command(name='ID', hidden=True)
@commands.is_owner()
async def get_id(ctx, member_id):
    guild = await client.fetch_guild(646164479863947266)
    member = await guild.fetch_member(member_id)
    if member is None:
        return await ctx.send(f"{member_id} not found in {guild}")
    return await ctx.send(Datetime.get_full_date(member.created_at))

@get_id.error
async def get_id_error(ctx, error):
    return await ctx.send(error.original.text)
"""


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
    print(f'Bot signed in as {client.user}')
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Game("@MakeShitFartist help")
    )


@client.command(hidden=True)
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("Logging off...")
    await ctx.bot.logout()


@shutdown.error
async def shutdown_error(ctx, error):
    return


"""@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.NotOwner):
        eql = "=" * 20
        author = f"{ctx.author} | ID: {ctx.author.id}"
        guild = f"{ctx.guild} | Guild ID: {ctx.guild.id}"
        info = f"{eql}\nUser: {author}\nGuild: {guild}\n{error}\n{eql}\n"
        return print(info)"""


with open('token') as tokenFile:
    client.run(tokenFile.read())
