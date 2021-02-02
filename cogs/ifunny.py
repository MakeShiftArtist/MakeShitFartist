import json
import praw
import discord
import asyncio
from random import randint
from ifunny import Client, objects
from discord.ext import commands
from definitions import *

class Logins:
    def __init__(self):
        with open("tokens.json") as f:
            data = json.load(f)
            self.bot = data["ifunny"]["bot"]
            self.reactions = data["ifunny"]["625719520127877136"]
            self.main = data["ifunny"]["386839413935570954"]
            self.reddit = data["reddit"]

accounts = Logins()
reddit = praw.Reddit(
    client_id=accounts.reddit["client_id"],
    client_secret=accounts.reddit["client_secret"],
    user_agent=accounts.reddit["user_agent"]
)
subreddit = reddit.subreddit('memes')

robot = Client(prefix="-")
robot.login(accounts.bot['email'], accounts.bot['password'])

reactions = Client(prefix="-")
reactions.login(accounts.reactions["email"], accounts.reactions["password"])

main_account = Client(prefix="-")
main_account.login(accounts.main["email"], accounts.main["password"])

file = "ifunnydiscord.sqlite"

verified = [
    '54deca36684fd0235b8b456e',
    '5ef252501348a65009117e97',
    '5f31c815ec5740655a61e46e',
    ]

def get_ifunny(data):
    user = objects.User.by_nick(data, client=robot)
    if user is None:
        user = objects.User.by_id(data, client=robot)
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

    def update(self, author_id=None, total=None):
        if total is None:
            total = self.total
        if author_id is None:
            author_id = self.author_id
        database = Database(file)
        database.cursor.execute(
            f'UPDATE Autoposts SET Total = {total} WHERE MemberID == {author_id};'
            )
        database.close()


class iFunny(commands.Cog):
    '''Commands for interacting with iFunny'''

    def __init__(self, bot):
        self.bot = bot
        self.auto = Autopost(robot, subreddit)
        self.autopost = autopost_info()
        self.database = Database(file)


    @commands.Cog.listener()
    async def on_ready(self):
        print('iFunny Cog loaded')

    @commands.command(
        name='Autopost',
        aliases=['ap'],
        hidden=True
        )
    @commands.is_owner()
    async def autopost_toggle(self, ctx):
        exists = self.database.get_select(
            f'SELECT * FROM Autoposts WHERE MemberID = {ctx.author.id};'
            )
        if exists is None:
            vals = (ctx.author.id, 0)
            self.database.cursor.execute(
                "INSERT INTO Autoposts (MemberID, Total)\nVALUES (?,?);",
                vals
                )
            self.database.save()
        if self.autopost.on is False:
            print("Autoposting...")
            embed = discord.Embed(
                title='Autoposted Started',
                description='Memes post every 5-15 minutes',
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            self.autopost.on = True
            while self.autopost.on:
                meme = await self.auto.get_meme()
                await self.auto.post_meme(meme)
                self.autopost.count += 1
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
                color=discord.Color.blue()
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
            self.database.cursor.execute(
                f'UPDATE Autoposts SET Total = {total} WHERE MemberID == {id};'
                )
            self.database.save()

    @autopost_toggle.error
    async def autopost_toggle_error(self, ctx, error):
        return await ctx.send(error)

    @commands.command(
        name='iFunnyuser',
        brief='Retrieves an iFunny profile',
        aliases=['if', 'ifuser'],
        help='Gets a info about an iFunny user.',
        usage='iFunnyuser [username]',
        )
    @commands.cooldown(1, 2.0, type=commands.BucketType.member)
    async def get_ifunny_user(self, ctx, *, username: str = None):
        if username is None:
            return await ctx.send(
                f"What's the iFunny account you wan't want me to find, {insult()}?"
                )
        embed = Embeds.loading("Finding user...")
        message = await ctx.send(embed=embed)
        user = get_ifunny(username)
        if user is None:
            embed = discord.Embed(
                title='Failed',
                description=f'{username} does not exist',
                color=discord.Color.red(),
                )
            return await message.edit(embed=embed)

        embed = iFunnyEmbeds.iFunnyUserEmbed(user)
        try:
            return await message.edit(embed=embed)
        except Exception:
            return await ctx.send(embed=embed)

    @get_ifunny_user.error
    async def get_ifunny_user_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            time = round(error.retry_after*100)/100
            return await ctx.send(
                f'Slow down, {insult()}.\nTry again in {time} seconds.'
                )
        else:
            embed = discord.Embed(
                title="Failed",
                description=error,
                color=discord.Color.red(),
                )
            return await ctx.send(embed=embed)

    @commands.command(
        name='Subscribe',
        aliases=['sub'],
        brief='Subscribes to an iFunny account',
        usage='subscribe [username]',
        help='This will make the bot subscribe to an iFunny account.',
        )
    @commands.cooldown(1, 5.0, commands.BucketType.member)
    async def subscribe_c(self, ctx, username=None):
        if username is None:
            return await ctx.send(
                f"Who the fuck do you want me to subscribe to, {insult()}?"
                )
        embed = discord.Embed(
            title='<a:loading:774385294106689557> Finding user...',
            color=discord.Color.blue(),
            )
        message = await ctx.send(embed=embed)
        user = get_ifunny(username)
        if user is None:
            embed = discord.Embed(
                title=f'{username} does not exist',
                color=discord.Color.red())
            await message.edit(embed=embed)
        elif user.is_subscription and user.id not in verified:
            embed = iFunnyEmbeds.iFunnySubEmbed(user, robot)
            user.unsubscribe()
            await message.edit(embed=embed)
        elif user.id in verified:
            embed = discord.Embed(
                title=f"No, {insult()}. That's my account",
                color=discord.Color.blue()
                )
            await message.edit(embed=embed)
        else:
            embed = iFunnyEmbeds.iFunnySubEmbed(user, robot)
            user.subscribe()
            await message.edit(embed=embed)

    @subscribe_c.error
    async def subscribe_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            time = round(error.retry_after*100)/100
            return await ctx.send(
                f'Slow down, {insult()}.\nTry again in {time} seconds.'
                )
        elif isinstance(error, commands.BadArgument):
            return await ctx.send("That's not a valid iFunny Account.")
        else:
            embed = discord.Embed(
                title="Failed",
                description="Subscription failed",
                color=discord.Color.red())
            embed.add_field(name="Reason", value=str(error))
            return await ctx.send(embed=embed)

    @commands.command(
        name='Smileposts',
        brief="Smiles an iFunny users posts",
        usage='Smileposts [username]',
        help='Smiles up to 50 posts from an iFunny profile. Ignores smiled posts',
        aliases=['smile', 'likeposts'],
        cooldown_after_parsing=True,
        )
    @commands.cooldown(2, 20.0, commands.BucketType.member)
    async def smileposts_c(self, ctx, username: str = None):
        if username is None:
            return await ctx.send("What account do you want me to smile?")
        embed = Embeds.loading(f"Finding {username}...")
        message = await ctx.send(embed=embed)
        user = get_ifunny(username)
        if user is None:
            embed = Embeds.custom_error(
                'User does not exist',
                'This needs an iFunny user to work.'
                )
            return await message.edit(embed=embed)

        embed = Embeds.loading(f"Smiling {user.nick}'s posts...")
        await message.edit(embed=embed)
        count = 0
        post_num = 0
        for post in user.timeline:
            post_num += 1
            if post.is_smiled:
                if post_num == 50:
                    break
                continue
            await asyncio.sleep(1)
            post.smile()
            count += 1
            if count == 50:
                break
        embed = discord.Embed(
            title=f'Finished smiling {count} posts from {user.nick}',
            description=f"{post_num} posts seen.",
            color=discord.Color.blue()
            )
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

    @commands.command(
        name="Post",
        hidden=True,
    )
    async def post_c(self, ctx):
        if ctx.author.id == 386839413935570954:
            poster = main_account
        elif ctx.author.id == 625719520127877136:
            poster = reactions
        else:
            return

        if not ctx.message.attachments and \
            not content_url:
            return await ctx.send("You need an attachment or link of what you want to post")

        links = ""
        count = 0
        message = await ctx.send(embed=Embeds.loading("Posting content..."))
        post = None

        for att in ctx.message.attachments:
            if post is not None:
                await asyncio.sleep(10)
            count+=1
            try:
                post = poster.post_url(
                    url=att.proxy_url,
                    wait=True,
                    timeout=60,
                )
                links += Format.hyperlink(f"Post #{count}", post.link) + "\n"
            except AttributeError as e:
                links += f"Post #{count} failed to post in 60 seconds\n"
            except Exception as e:
                print(e)
                await ctx.send(e)

        embed = discord.Embed(
            title="Links",
            description=links,
            color=discord.Color.blue(),
            timestamp=Datetime.timestamp(),
        )

        try:
            await message.edit(content=None, embed=embed)
        except Exception as e:
            print(e)
            print(type(e))
            await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(iFunny(bot))
