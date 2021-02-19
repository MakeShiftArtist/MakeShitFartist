import discord
import json
import asyncio
from discord.ext import commands
from main import _prefix_callable as PREFIX
from collections import Counter
from definitions import *
import re

file = "ifunnydiscord.sqlite"


class Misc(commands.Cog):
    '''Miscellaneous commands that don't really fit in a category'''

    def __init__(self, bot):
        self.bot = bot
        self.user_reacts = {
            420: "emoji"
        }
        self.deletes = {
        }
        self.edits = {
        }

    @commands.Cog.listener()
    async def on_ready(self):
        print('Misc Cog loaded')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id in self.user_reacts:
            try:
                await message.add_reaction(self.user_reacts[message.author.id])
            except Exception:
                return

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.id == self.bot.user.id:
            return

        atts = True
        for att in message.attachments:
            if re.match(r"\S.gif$|\S.jpg$|\S.png$", att.proxy_url):
                break
        else:
            atts = False

        if (not message.content and not atts):
            return

        info = {
            "message": message,
            "time": Datetime.timestamp(),
        }
        self.deletes[message.guild.id] = info

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.id == self.bot.user.id:
            return
        if not before.content:
            return
        try:
            current_guild = self.edits[before.guild.id]
            if before.id == current_guild["id"]:
                current_guild["extra"] = before
                current_guild["after"] = after
                return
        except KeyError:
            pass
        info = {
            "id": before.id,
            "before": before,
            "extra": None,
            "after": after,
            "time": Datetime.timestamp(),
        }
        self.edits[before.guild.id] = info

    @commands.command(
        name="Snipe",
        usage="snipe",
        help="Sends the most recently deleted message",
        brief="Snipes a deleted message",
        aliases=['s'],
        )
    async def snipe_c(self, ctx):
        try:
            info = self.deletes[ctx.guild.id]
            message = info["message"]
        except KeyError:
            return await ctx.send("Nothing to snipe!")
        embed = discord.Embed(
            description=message.content,
            color=discord.Color.blue(),
            timestamp=info["time"],
        ).set_author(
            name=message.author,
            icon_url=message.author.avatar_url
        )
        for pic in message.attachments:
            link = pic.proxy_url
            if not link:
                link = pic.url
            if re.match(r"\S.gif$|\S.jpg$|\S.png$", link):
                embed.set_image(url=link)
            break
        return await ctx.send(embed=embed)

    @commands.command(
        name="Editsnipe",
        usage="editsnipe",
        help="Sends the most recently edited message",
        brief="Snipes an edited message",
        aliases=["es"],
        )
    async def editsnipe_c(self, ctx):
        try:
            info = self.edits[ctx.guild.id]
            og = info["before"]
        except KeyError:
            return await ctx.send("Nothing to snipe!")
        embed = discord.Embed(
            title="Original",
            description=og.content,
            color=discord.Color.blue(),
            timestamp=info["time"],
        ).set_author(
            name=og.author,
            icon_url=og.author.avatar_url
        ).add_field(
            name="New",
            value=info["after"].content[:1023],
            inline=False,
        )
        if info["extra"] is not None:
            embed.insert_field_at(
                0,
                name="Previous Edit",
                value=info["extra"].content[:1023]
            )
        for pic in og.attachments:
            link = pic.proxy_url
            if not link:
                link = pic.url
            if re.match(r"\S.gif$|\S.jpg$|\S.png$", link):
                embed.set_image(url=link)
            break
        return await ctx.send(embed=embed)

    @commands.command(
        name='IP',
        brief="Sends info about an IP address",
        help="Sends an embed with all pubic info from an ip address",
        usage="ip [ip address]"
        )
    @commands.cooldown(2,10.0,type=commands.BucketType.member)
    async def ip_info(self, ctx, ip_address:str=None):
        if ip_address is None:
            return await ctx.send("You need to supply an IP address")
        embed = Embeds.loading()
        message = await ctx.send(embed=embed)
        ip = IPInfo(ip_address)
        if ip.is_success():
            info = ip.ip_info()
        else:
            info = ip.error()

        if ip.is_success():
            embed = Embeds.ip_embed(info)
        else:
            embed = Embeds.custom_error('IP info failed', info.message)
        try:
            return await message.edit(embed=embed)
        except Exception:
            return await ctx.send(message.edit)

    @ip_info.error
    async def ip_info_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            return
        return await ctx.send(error)


    @commands.command(
        name='Ping',
        brief='Checks bot latency',
        usage='Ping',
        help="Checks the bot's latency to the server in milliseconds",
    )
    async def ping_c(self, ctx):
        ping_embed = discord.Embed(
            title = f'Go fuck yourself! {round(self.bot.latency * 1000)}ms',
            color=discord.Color.blue()
            )
        await ctx.send(embed=ping_embed)


    @commands.command(
        name='Invite',
        brief='Sends an invite link',
        usage='Invite',
        help='Sends important invite links')
    async def invite_c(self, ctx):

        bot_link = "https://discord.com/oauth2/authorize?client_id="
        bot_link += "723105765812076664&scope=bot&permissions=2083912951"
        embed = discord.Embed(
            title='Invite links',
            description=f"[My bot's page](https://top.gg/bot/723105765812076664)",
            color=discord.Color.blue(),
            ).add_field(
            name='Bot invite',
            value=f'[Invite the bot]({bot_link})',
            inline=False,
            ).add_field(
            name='Support Server',
            value=f"[Get help here](https://discord.com/invite/4WGpdmE)",
            inline=False,
            )
        await ctx.send(embed=embed)

    @commands.command(
        name='User',
        brief='Gets basic user info',
        usage='User [@member]',
        help='This gets info about a discord user by mentioning them',
        )
    async def user_c(self, ctx, member : discord.Member=None):
        if member is None:
            member = ctx.author
        embed = Embeds.user_info(ctx, member)
        await ctx.send(embed=embed)

    @user_c.error
    async def user_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title='\U0000274c Bad Argument',
                description=f'You need to mention the user, {insult()}.',
                color=0xFF0000,
                )
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

    @commands.command(
        name='Prefix',
        brief="Sets the prefix for the server.",
        aliases=['SetPrefix'],
        help="Sets a specific prefix for the server",
        usage=f"Prefix [prefix]",
        )
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 10.0, commands.BucketType.guild)
    async def setprefix_c(self, ctx, *, prefix=None):
        if prefix is None:
            return await ctx.send(
                f"Hey, {insult()}. How do you expect me to change the prefix if you don't supply one?")
        if len(prefix) > 15:
            return await ctx.send(
                "That prefix is too long. Why the fuck would you want the prefix to be that long?")
        if "@everyone" in prefix or "@here" in prefix:
            return await ctx.send("Prefix can't have a default mention in it")
        guildid = ctx.message.guild.id
        db = Database(file)
        cursor = db.cursor
        current_prefix = PREFIX(self.bot, ctx.message)
        if (prefix == '-') and (current_prefix != '-'):
            cursor.execute(
                f'DELETE FROM GuildPrefixes\nWHERE (GuildID = "{guildid}")'
                )
            db.save()
            return await ctx.send('The prefix has been reset.')
        elif prefix == current_prefix:
            db.save()
            return await ctx.send(f"That's the same prefix, {insult()}.")
        else:
            cursor.execute(
                f'DELETE FROM GuildPrefixes\nWHERE (GuildID = "{guildid}")'
                )
            sql = 'INSERT INTO GuildPrefixes (GuildID, Prefix) VALUES (?,?)'
            values = (guildid, prefix)
            cursor.execute(sql, values)
            db.save()
            return await ctx.send(
                f'Prefix set as `{prefix}`.\nDon\'t forget it, {insult()}.'
                )

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

    @commands.command(
        name='Avatar',
        brief='Gets a users profile picture',
        usage='Avatar <@user>',
        help='Sends a users avatar in an embed',
        aliases=['av','pfp','profilepic'],
        )
    async def pfp_c(self, ctx, member:discord.Member=None):
        if member is None:
            member = ctx.message.author
        embed = discord.Embed(
            title="Avatar",
            color=discord.Color.blue()
            )
        embed.set_author(
            name=member.display_name,
            icon_url=member.avatar_url
            )
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

    @commands.command(
        name="Embed",
        brief="Creates a custom embed",
        help="Creates a custom embed with a title, description and fields.",
        usage="[title] <description>`\n> `<field title | field description>",
        )
    async def send_embed(self, ctx, title=None, *, desc=None):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        if title is None:
            return await ctx.send("You need a title for an embed")

        if desc is None:
            desc = ""
        extra = desc.split("\n")
        try:
            embed = discord.Embed(
                title=title,
                description=extra[0],
                color=discord.Color.blue(),
                timestamp=Datetime.timestamp()
                )
        except Exception:
            embed = discord.Embed(
                title=title,
                color=discord.Color.blue()
                )
        for field in extra[1:]:
            data = re.split(r"((?<!\\)(\s\|\s|\s\||\|\s|\|))", field)
            regex = re.compile(r'(\s\|\s|\s\||\|\s|\|)')
            filtered = [i for i in data if not regex.match(i)]
            if len(filtered) == 1:
                embed.add_field(
                    name="Field",
                    value=filtered[0],
                    inline=False
                    )
            else:
                if filtered[0] == "":
                    filtered[0] = "Field"
                if filtered[1] == "":
                    filtered[1] = "\u200B"
                embed.add_field(
                    name=filtered[0],
                    value="\n".join(filtered[1:]),
                    inline=False
                    )
        #embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=ctx.author)
        return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Misc(bot))
