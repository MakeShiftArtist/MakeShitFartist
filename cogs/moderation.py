import discord
import asyncio
from discord.ext import commands
from definitions import *


class MuteBase:

    def __init__(self, member):
        self.mute_role = None
        self.member = member
        self.guild = member.guild

    async def get_role(self):
        mute_role = discord.utils.get(self.guild.roles, name='In Brazil')

        if mute_role is None:
            mute_role = discord.utils.get(self.guild.roles, name='Muted')

        if mute_role is None:
            mute_role = discord.utils.get(self.guild.roles, name='Mute')

        self.mute_role = mute_role
        return mute_role

    async def make_role(self):
        await self.guild.create_role(name='In Brazil',
        reason="I couldn't find \"Muted\" or \"In Brazil\" role so I made my own")

        mute_role = discord.utils.get(self.guild.roles, name='In Brazil')

        mute_perms = discord.Permissions.none()
        await mute_role.edit(permissions=mute_perms)

        perms = discord.PermissionOverwrite()
        perms.send_messages = False
        for channel in self.guild.channels:
            try:
                await channel.set_permissions(mute_role, overwrite=perms)
            except:
                continue
        self.mute_role = mute_role
        return mute_role


    async def mute(self, reason=None):
        if reason is None:
            reason = f'{self.member} was muted'

        if self.mute_role is None:
            raise Exception("Mute role has not been retrieved yet")

        await self.member.add_roles(self.mute_role, reason=reason)

    async def unmute(self, reason=None):
        if reason is None:
            reason = f'{self.member} was unmuted'
        if self.mute_role is None:
            raise Exception("mute_role has not been retrieved yet")
        await self.member.remove_roles(self.mute_role, reason=reason)

def can_execute_action(ctx, user, target):
    return user.id == ctx.bot.owner_id or \
           user == ctx.guild.owner or \
           user.top_role > target.top_role

class ActionReason(commands.Converter):
    async def convert(self, ctx, argument='No reason given'):
        ret = f'**Mod:** {ctx.author} (**ID:** {ctx.author.id})\n**Reason:** {argument}'

        if len(ret) > 512:
            reason_max = 512 - len(ret) + len(argument)
            raise commands.BadArgument(f'Reason is too long ({len(argument)}/{reason_max})')
        return ret

class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        if argument.isdigit():
            member_id = int(argument, base=10)
            try:
                return await ctx.guild.fetch_ban(discord.Object(id=member_id))
            except discord.NotFound:
                raise commands.BadArgument('This member has not been banned before.') from None

        ban_list = await ctx.guild.bans()
        entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument('This member has not been banned before.')
        return entity

class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                member_id = int(argument, base=10)
                m = await resolve_member(ctx.guild, member_id)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
            except MemberNotFound:
                # hackban case
                return type('_Hackban', (), {'id': member_id, '__str__': lambda s: f'Member ID {s.id}'})()

        if not can_execute_action(ctx, ctx.author, m):
            raise commands.BadArgument('You cannot do this action on this user due to role hierarchy.')
        return m



class Moderation(commands.Cog):
    '''Commands for moderating the the server'''

    def __init__(self, bot):
        self.bot = bot
        self.db = Database("ifunnydiscord.sqlite")


    @commands.Cog.listener()
    async def on_ready(self):
        print('Moderation Cog loaded')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        is_muted = self.db.get_select(f'SELECT IsMuted FROM Mutes WHERE (GuildID = "{member.guild.id}" AND MemberID = "{member.id}")')
        if is_muted is None:
            return
        if is_muted:
            mutee = MuteBase(member)
            muted_role = await mutee.get_role()
            await mutee.mute(f'Automuted because {member} left to avoid mute')

    @commands.command(hidden=True, name='forceunmute')
    @commands.is_owner()
    @commands.dm_only()
    async def force_unmute(self, ctx, guildID:int, memberID:int=386839413935570954):
        try:
            guild = await self.bot.fetch_guild(guildID)
        except Exception as e:
            return await ctx.send(e)
        try:
            member = member = await guild.fetch_member(memberID)
        except Exception as e:
            return await ctx.send(e)
        if member is None:
            return await ctx.send(f"{memberID} is not in {guild}")
        try:
            mutee = MuteBase(member)
            await mutee.get_role()
            await mutee.unmute()
            return await ctx.send("Unmuted")
        except Exception as e:
            await ctx.send(e)

    @force_unmute.error
    async def force_unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(error)
        else:
            print(error)


    @commands.command(name='Stfu', aliases=['mute'], usage='stfu [@member] <reason>', brief='Mutes a member',
    help='Makes a user shut the fuck up. Tries to get a "Mute" or "In Brazil" role. Not my fault if you don\'t set the roles properly')
    @commands.has_permissions(manage_roles = True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute_c(self, ctx, member: discord.Member = None, *, reason:ActionReason=None):
        if member is None:
            return await ctx.send("Who the fuck do you want me to mute?")
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send("Their role is too high for me to mute them")
        elif member.top_role >= ctx.message.author.top_role:
            return await ctx.send("Their role is higher than yours lol")
        if reason is None:
            reason = f'**Mod:** {ctx.author} (**ID:** {ctx.author.id})\n**Reason:** No reason given'

        mutee = MuteBase(member)
        if mutee.mute_role is None:
            mute_role = await mutee.get_role()

        if mute_role is None:
            try:
                mute_role = await mutee.make_role()
            except:
                return await ctx.send("I don't have permission to make a mute role, and there's not one set up yet.")

        if mute_role in member.roles:
            return await ctx.send("They are already in Brazil (Muted)")

        if mute_role >= ctx.guild.me.top_role:
            return await ctx.send(f"{mute_role.name} is too high for me to give it to someone")
        await mutee.mute(reason)

        mod = ctx.message.author
        embed = discord.Embed(title=f"{member.display_name} muted by {mod}",
        description="Maybe now they'll shut the fuck up.", color=Common_info.blue)

        embed.add_field(name="Reason", value = reason)
        embed.set_footer(text=Datetime.get_full_date())
        await ctx.send(embed=embed)

        is_muted = self.db.get_select(f'SELECT IsMuted FROM Mutes WHERE (GuildID = "{member.guild.id}" AND MemberID = "{member.id}")')
        if is_muted is None or is_muted is False:
            sql = "INSERT INTO Mutes (GuildID, MemberID, IsMuted) VALUES(?,?,?)"
            values = (ctx.guild.id, member.id, True)
            self.db.cursor.execute(sql, values)
            self.db.save()


    @mute_c.error
    async def mute_c_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return
        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send("I can't edit people's roles")
        elif isinstance(error, commands.MemberNotFound):
            return await ctx.send(error)
        else:
            print(ctx.guild.name)
            print("Mute command error")
            print(error)
            return await ctx.send(error)

    @commands.command(name='Unmute', brief='Unmutes a member', usage='unmute [@member] <reason>',
    help="Allows someone to speak after you've made them stfu.")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute_c(self, ctx, member: discord.Member = None, *, reason:ActionReason=None):
        if member is None:
            return await ctx.send("Who the fuck do you want me to unmute?")
        if reason is None:
            reason = f'**Mod:** {ctx.author} (**ID:** {ctx.author.id})\n**Reason:** No reason given'
        mutee = MuteBase(member)
        mute_role = await mutee.get_role()
        if mute_role is None:
            return await ctx.send("You don't have a mute role setup. Use `stfu` or `mute` to set it up.")
        if mute_role not in member.roles:
            return await ctx.send("This member is not muted")
        if mute_role >= ctx.guild.me.top_role:
            return await ctx.send(f"{mute_role.name} is too high for me to remove it")
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(f'{member.name} has a higher role than me')
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("Their role is higher than yours lol")

        await mutee.unmute(reason)

        mod = ctx.message.author
        embed = discord.Embed(title=f"{member.display_name} unmuted by {mod}",
        description="Hopefully they've learned to shut the fuck up.", color=Common_info.blue)

        embed.add_field(name="Reason", value = reason)
        embed.set_footer(text=Datetime.get_full_date())
        await ctx.send(embed=embed)

        is_muted = self.db.get_select(f'SELECT IsMuted FROM Mutes WHERE (GuildID = "{member.guild.id}" AND MemberID = "{member.id}")')
        if is_muted == 1:
            sql = f'DELETE FROM Mutes\nWHERE (GuildID = "{ctx.guild.id}" AND MemberID = "{member.id}")'
            self.db.cursor.execute(sql)
            self.db.save()

    @unmute_c.error
    async def unmute_c_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return
        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send("I can't edit people's roles")
        elif isinstance(error, commands.MemberNotFound):
            return await ctx.send(error)
        else:
            print(ctx.guild.name)
            print("Unmute command error")
            print(error)
            return await ctx.send(error)




    @commands.command(name='Purge',brief='Bulk deletes messages', aliases=['clear'],
    help='Deletes multiple messages at once\n> Defaults to `5` if no amount is passed through', usage='purge [amount]')
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(2,5.0,type=commands.BucketType.guild)
    async def purge_c(self, ctx, amount : int = 5):
        if amount > 1000:
            amount = 1000
        elif amount < 0:
            amount = 0

        if amount == 0:
            return await ctx.send("I've deleted 0 messages. What did you expect from that?")

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        count = len(deleted)
        author = ctx.message.author
        embed = discord.Embed(title=f"{count} messages deleted", color = Common_info.blue)
        embed.add_field(name="Moderator", value = f"{author.mention}\n(ID: {author.id})", inline=False)
        embed.set_footer(text=Datetime.get_full_date())
        message = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        try:
            return await message.delete()
        except Exception:
            return None

    @purge_c.error
    async def purge_c_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            time = round(error.retry_after*100)/100
            title = '\U0000274c Command On Cooldown'
            reason = f'Slow down, {insult()}.\nTry again in {time} seconds.'
            embed = discord.Embed(title=title, description=reason, color=Common_info.red)
            return await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = Embeds.custom_error("Bad Argument", f"That isn't a number, {insult()}.")
            return await ctx.send(embed=embed)
        else:
            command = "Purge"
            handle = Embeds.error_handler(ctx, error, commands, command)
            embed = handle[0]
            log_embed = handle[1]
            if log_embed is not None:
                channel = await self.bot.fetch_channel(768271364271898624)
                await channel.send(embed=log_embed)
            return await ctx.send(embed=embed)


    @commands.command(name='Ban',brief='Bans a member',help='Bans a member from the server', usage=f'Ban [@member]')
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban_c(self, ctx, member: MemberID=None, *, reason: ActionReason = None):
        if member is None:
            embed = Embeds.custom_error("Who?",f'Who the fuck do you expect me to ban, {insult()}?')
            return await ctx.send(embed=embed)
        bot = ctx.guild.me
        if member.top_role >= bot.top_role:
            embed= Embeds.custom_error("Missing Permissions",
            f"{member.mention}'s role is too high for me to ban them, {insult()}.")
            return await ctx.send(embed=embed)
        if reason is None:
            reason = f'Action done by {ctx.author} (ID: {ctx.author.id})'

        await ctx.guild.ban(member, reason=reason)
        embed = Embeds.moderation_success(ctx, member, 'Ban', reason)
        return await ctx.send(embed=embed)


    @ban_c.error
    async def ban_c_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = Embeds.custom_error("Who?",f'Try mentioning the user, {insult()}.')
            return await ctx.send(embed=embed)
        else:
            command = "Ban"
            handle = Embeds.error_handler(ctx, error, commands, command)
            embed = handle[0]
            log_embed = handle[1]
            if log_embed is not None:
                channel = await self.bot.fetch_channel(768271364271898624)
                await channel.send(embed=log_embed)
            return await ctx.send(embed=embed)


    @commands.command(name='Unban',brief='Unbans a member',
    help='Unbans a member from the server', usage=f'Unban [username#1234]')
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def unban_c(self, ctx, member: BannedMember, *, reason: ActionReason = None):
        if reason is None:
            reason = f'**Mod:** {ctx.author} **ID:** {ctx.author.id}: No reason given'

        await ctx.guild.unban(member.user, reason=reason)
        if member.reason:
            action = f'Unbanned {member.user} (ID: {member.user.id})\nBan reason: {member.reason}.'
        else:
            action = f'Unbanned {member.user} (ID: {member.user.id}).'
        embed = discord.Embed(title='\U00002705 User was unbanned', description=action, color=Common_info.blue)
        embed.add_field(name="Moderator:",value=reason)
        return await ctx.send(embed=embed)




    @unban_c.error
    async def unban_c_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = Embeds.custom_error("Who?",f"I can't find that user in the banned list, {insult()}. Wanna try again?")
            return await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = Embeds.custom_error("Who?",f'Who the fuck do you expect me to unban, {insult()}?')
            return await ctx.send(embed=embed)
        else:
            command = "Unban"
            handle = Embeds.error_handler(ctx, error, commands, command)
            embed = handle[0]
            log_embed = handle[1]
            if log_embed is not None:
                channel = await self.bot.fetch_channel(768271364271898624)
                await channel.send(embed=log_embed)
            return await ctx.send(embed=embed)


    @commands.command(name='Kick',brief='Kicks a member',help='Kicks a member from the server', usage=f'Kick [@member]')
    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick_c(self, ctx, member: discord.Member, *, reason=None):
        bot = ctx.guild.me
        if member.top_role >= bot.top_role:
            embed= Embeds.custom_error("Missing Permissions",
            f"{member.mention}'s role is too high for me to kick them, {insult()}.")
            return await ctx.send(embed=embed)
        if member not in ctx.guild.members:
            kick_embed = discord.Embed(title=f'\U0000274c {member} wasn\'t found. Maybe try mentioning them?', color=Common_info.red)
            return await ctx.send(embed=kick_embed)
        if member.guild_permissions.ban_members == True:
            kick_embed = discord.Embed(title=f'\U0000274c I can\'t kick mods, {insult()}', color=Common_info.red)
            return await ctx.send(embed=kick_embed)
        await member.kick(reason=reason)
        if member not in ctx.guild.members:
            kick_embed = discord.Embed(title=f'\U00002705 {member} was kicked by {ctx.message.author}', color=Common_info.blue)
            return await ctx.send(embed=kick_embed)


    @kick_c.error
    async def kick_c_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            time = round(error.retry_after*100)/100
            title = '\U0000274c Command On Cooldown'
            reason = f'Slow down, {insult()}.\nTry again in {time} seconds.'
            embed = discord.Embed(title=title, description=reason, color=Common_info.red)
            return await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = Embeds.custom_error("Who?",f'Try mentioning the user, {insult()}.')
            return await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = Embeds.custom_error("Who?",f'Who the fuck do you expect me to kick, {insult()}?')
            return await ctx.send(embed=embed)
        else:
            command = "Kick"
            handle = Embeds.error_handler(ctx, error, commands, command)
            embed = handle[0]
            log_embed = handle[1]
            if log_embed is not None:
                channel = await self.bot.fetch_channel(768271364271898624)
                await channel.send(embed=log_embed)
            return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(moderation(bot))
