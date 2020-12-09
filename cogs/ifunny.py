""" iFunny imports """
from ifunny import Client, objects
from random import randint
import praw
import discord
import asyncio
from discord.ext import commands
from definitions import Database, Datetime, Autopost, Common_info, Embeds
from definitions import insult, iFunny

reddit = praw.Reddit(
    client_id='id',
    client_secret='secret',
    user_agent='Discord/iFunny/Reddit Bot'
)
subreddit = reddit.subreddit('memes')

file = "ifunnydiscord.sqlite"

robot = Client(prefix="-")
robot.login("email", "password")

verified = [
    '54deca36684fd0235b8b456e',
    '5ef252501348a65009117e97',
    '5f31c815ec5740655a61e46e'
    ]


""" Discord Imports """


def get_ifunny(data):
    user = objects.User.by_nick(data, client=robot)
    if user is None:
        try:
            user = objects.User(id=data, client=robot)
            if user.nick:
                return user
        except Exception:
            return None
    return user


class autopost_info:
    """SELECT Total FROM Autoposts
    WHERE (MemberID ="386839413935570954")"""

    def __init__(self):
        self.author_id = 386839413935570954
        self.on = False
        self.count = 0
        database = Database(file)
        total = database.get_select(self.__doc__)
        self.total = total
        database.close()

    def get_total(self):
        database = Database(file)
        total = database.get_select(self.__doc__)
        self.total = total
        database.close()
        return self.total

    def update(self, total=None, author_id=None):
        if total is None:
            total = self.total
        if author_id is None:
            author_id = self.author_id



@robot.event(name="on_connect")
def _connected_to_chat(data):
    print(f"Logged into {robot.nick}")
    print(Datetime.get_full_date(Datetime.now()))


class ifunny(commands.Cog, name='iFunny'):
    '''Commands for interacting with iFunny'''

    def __init__(self, bot):
        self.bot = bot
        self.auto = Autopost(robot, subreddit)
        self.autopost = autopost_info()
        self.database = Database(file)

    @commands.Cog.listener()
    async def on_ready(self):
        print('iFunny Cog loaded')

    @commands.command(name='Autopost', hidden=True)
    @commands.is_owner()
    async def autopost_toggle(self, ctx):
        if self.autopost.on is False:
            print("Autoposting...")
            embed = discord.Embed(
                title='Autoposted Started',
                description='Memes post every 5-15 minutes',
                color=Common_info.blue
            )
            await ctx.send(embed=embed)
            self.autopost.on = True
            while self.autopost.on:
                meme = await self.auto.get_meme()
                await self.auto.post_meme(meme)
                self.autopost.count +=1
                print(f"{self.autopost.count} meme(s) posted")
                total = self.autopost.get_total()
                id = ctx.author.id
                self.database.cursor.execute(
                    f'UPDATE Autoposts SET Total = {total} WHERE MemberID == {id};'
                    )
                self.database.save()
                wait_time = randint(5, 15)
                await asyncio.sleep(60*wait_time)
        else:
            print('Autopost stopped.')
            embed = discord.Embed(
                title='Autoposted Stopped',
                description=f'Autoposted `{self.autopost.count}` meme(s)',
                color=Common_info.blue
            )
            self.autopost.total += self.autopost.count
            embed.add_field(
                name='Total memes posted',
                value=f"`{self.autopost.total}`"
            )
            self.autopost.count = 0
            await ctx.send(embed=embed)
            self.autopost.on = False
            total = self.autopost.get_total()
            id = ctx.author.id
            self.database.cursor.execute(f'UPDATE Autoposts SET Total = {total} WHERE MemberID == {id};')
            self.database.save()

    @autopost_toggle.error
    async def autopost_toggle_error(self, ctx, error):
        return await ctx.send(error)


    @commands.command(
        name='iFunnyuser',
        brief='Retrieves an iFunny profile', aliases=['if', 'ifuser'],
        help='Gets a info about an iFunny user.',
        usage='iFunnyuser [username]')
    @commands.cooldown(1, 2.0, type=commands.BucketType.member)
    async def get_ifunny_user(self, ctx, username: str = None):
        if username is None:
            return await ctx.send(f"What's the iFunny account you wan't want me to find, {insult()}?")
        embed = discord.Embed(title='<a:loading:774385294106689557> Finding user...', color=Common_info.blue)
        message = await ctx.send(embed=embed)
        user = get_ifunny(username)
        if user is None:
            embed = discord.Embed(title='Failed', description=f'{username} does not exist', color=0xFF0000)
            return await message.edit(embed=embed)

        embed = iFunny.iFunnyUserEmbed(user)
        return await message.edit(embed=embed)

    @get_ifunny_user.error
    async def get_ifunny_user_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            time = round(error.retry_after*100)/100
            return await ctx.send(f'Slow down, {insult()}.\nTry again in {time} seconds.')
        else:
            embed = discord.Embed(title="Failed", description=error, color=0xFF0000)
            return await ctx.send(embed=embed)

    @commands.command(name = 'Subscribe',brief = 'Subscribes to an iFunny account', aliases=['sub'],
    help='This will make the bot subscribe to an iFunny account.',usage='subscribe [username]')
    @commands.cooldown(1,5.0,commands.BucketType.member)
    async def subscribe_c(self, ctx, username=None):
        if username is None:
            return await ctx.send(f"Who the fuck do you want me to subscribe to, {insult()}?")
        embed = discord.Embed(title='<a:loading:774385294106689557> Finding user...', color=Common_info.blue)
        message = await ctx.send(embed=embed)
        user = get_ifunny(username)
        if user is None:
            embed = discord.Embed(title=f'{username} does not exist', color=Common_info.red)
            await message.edit(embed=embed)
        elif user.is_subscription and user.id not in verified:
            embed = iFunny.iFunnySubEmbed(user, robot)
            user.unsubscribe()
            await message.edit(embed=embed)
        elif user.id in verified:
            embed = discord.Embed(title=f"No, {insult()}. That's my account", color=Common_info.blue)
            await message.edit(embed=embed)
        else:
            embed = iFunny.iFunnySubEmbed(user, robot)
            user.subscribe()
            await message.edit(embed=embed)

    @subscribe_c.error
    async def subscribe_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            time = round(error.retry_after*100)/100
            return await ctx.send(f'Slow down, {insult()}.\nTry again in {time} seconds.')
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("That's not a valid iFunny Account.")
        else:
            embed = discord.Embed(title="Failed", description="Subscription failed", color=0xFF0000)
            embed.add_field(name="Reason", value=str(error))
            return await ctx.send(embed=embed)

    @commands.command(name='Smileposts', brief="Smiles an iFunny users posts", usage='Smileposts [username]',
    help='Smiles/likes up to 50 posts from an iFunny profile. If a post is already smiled, it ignores it.',
    aliases=['smile', 'likeposts'], cooldown_after_parsing=True)
    @commands.cooldown(1,10.0,commands.BucketType.member)
    async def smileposts_c(self, ctx, username:str=None):
        if username is None:
            return await ctx.send("What account do you want me to smile?")
        embed = discord.Embed(title='<a:loading:774385294106689557> Finding user...', color=Common_info.blue)
        message = await ctx.send(embed=embed)
        user = get_ifunny(username)
        if user is None:
            embed = Embeds.custom_error('User does not exist', 'This needs an iFunny user to work.')
            return await message.edit(embed=embed)

        embed = discord.Embed(title=f"<a:loading:774385294106689557> Smiling {user.nick}'s posts...", color=Common_info.blue)
        await message.edit(embed=embed)
        count = 0
        post_num=0
        for post in user.timeline:
            post_num+=1
            if post.is_smiled:
                if post_num == 50:
                    break
                continue
            await asyncio.sleep(1)
            post.smile()
            count+=1
            if count == 50:
                break
        embed = discord.Embed(title=f'Finished smiling {count} posts from {user.nick}', color=Common_info.blue)
        return await message.edit(embed=embed)

    @smileposts_c.error
    async def smileposts_c_error(self, ctx, error):
        command = "Smileposts"
        handle = Embeds.error_handler(ctx, error, commands, command)
        embed = handle[0]
        log_embed = handle[1]
        if log_embed is not None:
            channel = await self.bot.fetch_channel(768271364271898624)
            await channel.send(embed=log_embed)
        return await ctx.send(embed=embed)

    @commands.command(name='Unsmile', hidden=True)
    @commands.is_owner()
    async def unsmile_c(self, ctx, username:str = None, amount = 50):
        if username is None:
            return await ctx.send('What account do you want me to unsmile?')
        embed = discord.Embed(title='<a:loading:774385294106689557> Finding user...', color=Common_info.blue)
        message = await ctx.send(embed=embed)
        user = get_ifunny(username)
        if user is None:
            embed = discord.Embed(title='Failed', description=f'{username} does not exist', color=0xFF0000)
            return await message.edit(embed=embed)
        embed = discord.Embed(title=f"<a:loading:774385294106689557> Unsmiling {user.nick}'s posts...", color=Common_info.blue)
        await message.edit(embed=embed)
        count = 0
        post_num=0
        for post in user.timeline:
            post_num+=1
            if post.is_unsmiled:
                if post_num == amount:
                    break
                continue
            await asyncio.sleep(1)
            post.unsmile()
            count+=1
            if count == amount:
                break
        embed = discord.Embed(title=f'Finished unsmiling {count} posts from {user.nick}', color=Common_info.blue)
        return await message.edit(embed=embed)




def setup(bot):
    bot.add_cog(ifunny(bot))
