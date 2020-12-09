import discord
import asyncio
from discord.ext import commands
from main import _prefix_callable as PREFIX
from collections import Counter
from definitions import *
import re

file = "ifunnydiscord.sqlite"

data = Common_info.trello
trello_client = Trello.Info.client(data.api_key, data.api_secret, data.token)
base = Trello.Base(trello_client, "iMonke Development", "TRIAGE")


class misc(commands.Cog, name='Misc'):
    '''Miscellaneous commands that don't really fit in a category'''

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Misc Cog loaded')


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 741681680296706098:
            await message.add_reaction('<:extra_letter_i:767997424987537493>')
            await message.add_reaction('❤️')
            await message.add_reaction('🇸')
            await message.add_reaction('🇭')
            await message.add_reaction('🇮')
            await message.add_reaction('🇫')
            await message.add_reaction('🇹')

    @commands.command(hidden=True, name='IP')
    @commands.is_owner()
    async def ip_info_c(self, ctx, ip_address:str=None):
        if ip_address is None:
            return await ctx.send("You need to supply an IP address")
        embed = Embeds.loading()
        message = await ctx.send(embed=embed)
        api = IPInfo(ip_address)
        success = api.is_success()
        if success:
            info = api.ip_info()
        else:
            info = api.error()

        if success:
            embed = Embeds.ip_embed(info)
        else:
            embed = Embeds.custom_error('IP info failed', info.message)
        return await message.edit(embed=embed)

    @ip_info_c.error
    async def ip_info_c_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            return
        return await ctx.send(error)




    @commands.command(name='Trello', brief="Creates a report for iMonke",
    help= "Sends a report to [iMonke's Trello board](https://trello.com/b/6VnXOnCr/imonke-development)\n> Use `-trello` for a list of labels and more info\n> You must be in iMonke to use this command.",
    aliases=['report', 'bug', 'feature', 'feat'], usage='trello <labels> [title]`\n> `<description>')
    @commands.guild_only()
    @commands.cooldown(4, 20.0, commands.BucketType.member)
    async def trello_add_card(self, ctx, *, report:str=None):
        if ctx.guild.id != 646164479863947266:
            return await ctx.send("You must be in iMonke to use this command.")
        if report is None:
            embed = Embeds.trello_embed(base)
            return await ctx.send(embed=embed)
        embed = Embeds.loading()
        message = await ctx.send(embed=embed)

        fields = re.split('\n', report)
        if ctx.invoked_with == 'feature':
            ctx.invoked_with = 'feat'
        fields[0] += f" [{ctx.invoked_with}] "

        temp_desc = Format.trello_description(fields)
        bug_info = Trello.Card_labels(fields[0])
        if bug_info.title == '':
            embed = Embeds.custom_error("You need a title to report bugs or request features", report)
            return await message.edit(embed=embed)
        trello_desc = f"**Reporter:** `{ctx.author}`\n{temp_desc}\n\n[Message embed]({message.jump_url})"
        card = base.add_bug(fields[0] , trello_desc, bug_info.labels)
        time = Datetime.get_full_date()
        embed= discord.Embed(title='Trello report added to TRIAGE', description=f"[The report]({card.short_url})", color=Common_info.blue)
        embed.add_field(name='Title', value=bug_info.title, inline=False)

        labels = ''
        active_labels = Trello.Info.labels_with_names(base, bug_info.labels)
        for label in active_labels:
            labels+=f"`[{label.name}]` "
        if labels != '':
            embed.add_field(name='Tags/Labels', value=labels, inline=False)

        discord_desc = f"**Reporter:** {ctx.author.mention}\n{temp_desc}"
        embed.add_field(name='Description', value=discord_desc, inline=False)
        embed.set_footer(text=time)
        try:
            return await message.edit(embed=embed)
        except:
            return await ctx.send(embed=embed)

    @trello_add_card.error
    async def trello_add_card_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            time = round(error.retry_after*100)/100
            title = '\U0000274c Command On Cooldown'
            reason = f'Slow down, {insult()}.\nTry again in {time} seconds.'
            embed = discord.Embed(title=title, description=reason, color=Common_info.red)
            return await ctx.send(embed=embed)
        if isinstance(error, commands.NoPrivateMessage):
            return await ctx.send("You must be in iMonke to use this command.")
        command = "Trello"
        handle = Embeds.error_handler(ctx, error, commands, command)
        embed = handle[0]
        log_embed = handle[1]
        if log_embed is not None:
            channel = await self.bot.fetch_channel(768271364271898624)
            await channel.send(embed=log_embed)
        return await ctx.send(embed=embed)


    @commands.command(name='Ping',brief='Checks bot latency', usage='Ping',
    help="Checks the bot's latency to the server in milliseconds")
    async def ping_c(self, ctx):
        ping_embed = discord.Embed(title = f'Pong! {round(self.bot.latency * 1000)}ms', color=Common_info.blue)
        await ctx.send(embed=ping_embed)


    @commands.command(name='Invite',brief='Sends an invite link', usage='Invite',
    help='Sends an invite link to the channel so you can invite the bot to your server')
    async def invite_c(self, ctx):
        bot_link = 'https://discord.com/oauth2/authorize?client_id=723105765812076664&scope=bot&permissions=2083912951'
        embed = discord.Embed(title='Invite links',description=f"[My bot's page](https://top.gg/bot/723105765812076664)",color=Common_info.blue)
        embed.add_field(name='Bot invite', value=f'[Have it join your server here]({bot_link})', inline=False)
        embed.add_field(name='Support Server', value=f"[Get help here](https://discord.com/invite/4WGpdmE)", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='User',brief='Gets basic user info', usage='User [@member]',
    help='This gets info about a discord user by mentioning them')
    async def user_c(self, ctx, member : discord.Member=None):
        if member is None:
            member = ctx.author
        embed = Embeds.user_info(ctx, member)
        await ctx.send(embed=embed)

    @user_c.error
    async def user_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            title = '\U0000274c Bad Argument'
            embed = discord.Embed(title=title, description=f'You need to mention the user, {insult()}.', color=0xFF0000)
            return await ctx.send(embed=embed)
        else:
            command = "User"
            handle = Embeds.error_handler(ctx, error, commands, command)
            embed = handle[0]
            log_embed = handle[1]
            if log_embed is not None:
                channel = await self.bot.fetch_channel(768271364271898624)
                await channel.send(embed=log_embed)
            return await ctx.send(embed=embed)

    @commands.command(name='Prefix',brief="Sets the prefix for the server.", aliases=['SetPrefix'],
    help="Sets a specific prefix for the server",usage=f"Prefix [prefix]")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10.0, commands.BucketType.guild)
    async def setprefix_c(self, ctx, prefix=None):
        if prefix is None:
            return await ctx.send(f"Hey, {insult()}. How do you expect me to change the prefix if you don't supply one?")
        prefix = Format.prefix(prefix)
        if len(prefix) > 15:
            return await ctx.send("That prefix is too long. Why the fuck would you want the prefix to be that long?")
        guildid = ctx.message.guild.id
        db = Database(file)
        cursor = db.cursor
        current_prefix = PREFIX(self.bot, ctx.message)
        if (prefix == '-') and (current_prefix != '-'):
            cursor.execute(f'DELETE FROM GuildPrefixes\nWHERE (GuildID = "{guildid}")')
            db.save()
            return await ctx.send('The prefix has been reset.')
        elif prefix == current_prefix:
            db.save()
            return await ctx.send(f"That's the same prefix, {insult()}.")
        else:
            cursor.execute(f'DELETE FROM GuildPrefixes\nWHERE (GuildID = "{guildid}")')
            sql = 'INSERT INTO GuildPrefixes (GuildID, Prefix) VALUES (?,?)'
            values = (guildid, prefix)
            cursor.execute(sql, values)
            db.save()
            return await ctx.send(f'Prefix set as `{prefix}`.\nDon\'t forget it, {insult()}.')

    @setprefix_c.error
    async def setprefix_error(self, ctx, error):
        command = "Prefix"
        handle = Embeds.error_handler(ctx, error, commands, command)
        embed = handle[0]
        log_embed = handle[1]
        if log_embed is not None:
            channel = await self.bot.fetch_channel(768271364271898624)
            await channel.send(embed=log_embed)
        return await ctx.send(embed=embed)

    @commands.command(name='Avatar', brief='Gets a users profile picture', usage='Avatar <@user>',
    help='Sends a users avatar in an embed', aliases=['av','pfp','profilepic'])
    async def pfp_c(self, ctx, member:discord.Member=None):
        if member is None:
            member = ctx.message.author
        embed = discord.Embed(title="Avatar", color=Common_info.blue)
        embed.set_author(name=member.display_name,icon_url=member.avatar_url)
        embed.set_footer(text=f"ID: {member.id}")
        embed.set_image(url=member.avatar_url)
        return await ctx.send(embed=embed)

    @pfp_c.error
    async def pfp_c_error(self, ctx, error):
        command = "Avatar"
        handle = Embeds.error_handler(ctx, error, commands, command)
        embed = handle[0]
        log_embed = handle[1]
        if log_embed is not None:
            channel = await self.bot.fetch_channel(768271364271898624)
            await channel.send(embed=log_embed)
        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(misc(bot))
