import discord
from discord.ext import commands
from main import _prefix_callable as prefix_get

def is_ifunny_cog(string):
    new = ''.join([string[:1].lower(), string[1].upper(), string[2:].lower()])
    if new == 'iFunny':
        return True
    return False

def make_ifunny_cog(string):
    return ''.join([string[:1].lower(), string[1].upper(), string[2:].lower()])

def default_help(self, prefix, failed=None):
    embed=discord.Embed(title='Help', description=f"> `[arg]` = Required argument\n> `<arg>` = Not required\n> Try using `{prefix}help <category>` for more info",color=0x1E90FF)
    if failed is not None:
        field =f'{failed} is not a valid category or command'
        embed.add_field(name='Argument Error', value=field, inline=False)
    for cog in self.bot.cogs:
        if cog != 'Help':
            cog_desc = f'> {self.bot.cogs[cog].__doc__}'
            embed.add_field(name=cog, value=cog_desc, inline=False)
    return embed

def required_perms(command:str):
    command.capitalize()
    requires = {
        'Ban': 'Ban Members', 'Purge': 'Manage Messages',
        'Kick': 'Kick Members', 'Unban' : 'Ban Members',
        'Prefix': 'Manage Server', "Stfu" : "Manage Roles"
        }
    try:
        required = requires[command]
    except:
        required = None
    return required

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Help Cog loaded')

    @commands.command(hidden=True)
    async def help(self, ctx, arg='help'):
        if arg.lower() == 'mod':
            arg = 'Moderation'
        prefix = prefix_get(self, ctx.message)
        if arg is None or arg.lower() == 'help':
            embed = default_help(self, prefix)
            app = await self.bot.application_info()
            embed.set_footer(text=f'Bot by {app.owner}')
            return await ctx.send(embed=embed)


        elif arg.capitalize() in self.bot.cogs or is_ifunny_cog(arg):
            cog = self.bot.get_cog(arg.capitalize())
            if cog is None:
                cog = self.bot.get_cog(make_ifunny_cog(arg))
            embed = discord.Embed(title=cog.qualified_name,description=f'> {cog.__doc__}\n> Try using `{prefix}help <command>` for more info',color=0x1E90FF)
            commands = cog.get_commands()
            for command in commands:
                if not command.hidden:
                    embed.add_field(name=command.name,value=command.brief, inline=False)
            app = await self.bot.application_info()
            embed.set_footer(text=f'Bot by {app.owner}')
            return await ctx.send(embed=embed)

        else:
            command = self.bot.get_command(arg.capitalize())
            if command is not None:
                if command.hidden:
                    embed = default_help(self, prefix, failed=arg)
                    app = await self.bot.application_info()
                    embed.set_footer(text=f'Bot by {app.owner}')
                    return await ctx.send(embed=embed)

                embed=discord.Embed(title=f'{command.name}', description=f'> {command.help}',color=0x1E90FF)
                embed.add_field(name='Usage:',value=f'> `{prefix}{command.usage}`',inline=False)
                requires = required_perms(command.name)
                if requires is not None:
                    embed.add_field(name='Requires permission:',value=f'> `{requires}`',inline=False)
                if command.aliases != []:
                    alias = ''
                    for i in command.aliases:
                        if i == command.aliases[-1]:
                            alias+=f'`{i}`'
                        else:
                            alias+=f'`{i}` | '
                    embed.add_field(name='Alias(es):', value=alias, inline=False)
                app = await self.bot.application_info()
                embed.set_footer(text=f'Bot by {app.owner}')
                return await ctx.send(embed=embed)

            embed = default_help(self, prefix, failed=arg)
            app = await self.bot.application_info()
            embed.set_footer(text=f'Bot by {app.owner}')
            return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(help(bot))
