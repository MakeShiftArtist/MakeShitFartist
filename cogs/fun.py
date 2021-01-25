import games
import discord
import asyncio
from discord.ext import commands
from definitions import *
from ifunny import objects
import random
import praw
import re


class Fun(commands.Cog):
    '''Commands to add some fun to your server'''
    def __init__(self, bot):
        self.tictac = games.TicTacToe()
        self.bot = bot
        self.insult = Insults()
        self.names = {
            "walk": "walkstr8t",
            "soba": "cold..soba",
            "ella": "ellamenope",
            "child": "creature",
            "cweature": "creature",
            "kierkegaard": "creature",
            "wife-e": "macey",
            "wife": "macey",
            "meika_": "meika",
            "nabb-e": "nabbit",
            "shift": "makeshiftartist",
            "makeshift": "makeshiftartist",
        }
        self.friends = {
            "defy": {
                "message": "fuck me",
                "reacts": ["👉", "👌"],
                "id": 625719520127877136,
            },
            "walkstr8t": {
                "message": "put on the cat ears",
                "reacts": [u"\U0001f43e"],
                "id": 456972240311943170,
            },
            "cesar": {
                "message": "Shut the fuck up",
                "reacts": ["<a:spinpikachu:796939118571421747>"],
                "id": 691099809720958980,
            },
            "cold..soba": {
                "message": "Put on the maid outfit ",
                "reacts": [u"\U0001f52b"],
                "id": 773690510698741760,
            },
            "creature": {
                "message": "lblblbllblblllbllbllblblbl",
                "reacts": [u"\U0000fe0f"],
                "id": 425665226721984514,
            },
            "macey": {
                "message": "*Gay screams*",
                "reacts": [u"\U0001F3F3\uFE0F\u200D\U0001F308"],
                "id": 756323850257563709,
            },
            "meika": {
                "message": "**pisses aggressively**",
                "reacts": ["<:doitagain:798790082009235476>"],
                "id": 527342369729806336,
            },
            "nabbit": {
                "message": "I'm fast. Faster than you. That's all you need to know",
                "reacts": [u"\U0001f344"],
                "id": 651244875915853825,
            },
            "ellamenope": {
                "message": "ily \U0001f642 hugs",
                "reacts": [u"\U0001f49c"],
                "id": 645783211955322961,
            },
            "makeshiftartist": {
                "message": "Your toes, hand 'em over",
                "reacts": [u"\U0001f608"],
                "id": 386839413935570954,
            },
        }

    @commands.Cog.listener()
    async def on_ready(self):
        print('Fun Cog loaded')

    @commands.command(
        name="friend",
        hidden=True,
        aliases=[
            "walkstr8t", "walk", "defy", "cesar",
            "ella", "ellamenope", "soba", "cold..soba",
            "child", "creature", "cweature", "kierkegaard",
            "macey", "wife-e", "meika", "meika_",
            "nabbit", "nabb-e", "shift", "makeshift",
            "makeshiftartist",
            ]
        )
    @commands.bot_has_permissions(manage_webhooks=True)
    async def fren_c(self, ctx):
        name = ctx.invoked_with.lower()
        if name in self.names:
            name = self.names[name]

        if name in self.friends:
            webhooks = await ctx.channel.webhooks()

            webhook = discord.utils.get(webhooks, name="MakeShitFartist")

            if not webhook:
                webhook = await ctx.channel.create_webhook(name="MakeShitFartist")

            friend = self.friends[name]
            user = await self.bot.fetch_user(friend["id"])
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass
            msg = await webhook.send(
                friend["message"],
                username=user.display_name,
                avatar_url=user.avatar_url,
                wait=True
                )
            try:
                for reaction in friend["reacts"]:
                    await msg.add_reaction(reaction)
            except Exception as e:
                print(e)
    @fren_c.error
    async def fren_c_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(error)


    @commands.command(
        name='Minesweeper',
        brief='Sends a minesweeper game',
        help='Sends a game of Minesweeper using spoilers.',
        aliases=['MS', 'Minespoiler'],
        usage='Minesweeper <size> <bombs>',
        )
    async def minesweeper_c(self, ctx, size=8, bombs=8):
        if size < 2:
            size = 2
        if size > 13:
            size = 13
        if bombs >= (size * size) - 1:
            bombs = (size * size) - 1
        board = games.Minesweeper.draw(size, size, bombs)
        await ctx.send(
            f'**Minesweeper: {size} by {size} with {bombs} total bombs.\n{board}**'
            )


    @minesweeper_c.error
    async def minesweeper_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send('That\'s not a number you baboon')

    @commands.command(name='Bubblewrap',brief='Sends bubble wrap',
        help='This will send bubble wrap ising spoilers.\n> Pretty simple really.',
        usage='Bubblewrap <amount>', aliases=['Pop', 'Bubble']
        )
    async def bubblewrap_c(self, ctx, amount=5):
        if amount > 13:
            amount = 13
        elif amount < 1:
            amount = 1
        pops = f'||pop||' * amount
        pops = f'{pops}\n' * amount
        return await ctx.send(f'**Bubble Wrap:**\n{pops}')

    @bubblewrap_c.error
    async def bubblewrap_c_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send(f"Size has to be an integer, {insult()}.")
        else:
            print(error)


    @commands.command(
        name='Roll',brief='Rolls a die',
        usage='Roll <sides>',
        help='Will give you a random number and whatever you input.'
        )
    async def roll_c(self, ctx, sides = 6.0):
        try:
            sides = abs(sides)
            sides = int(round(float(sides)))
            if sides < 2:
                sides = 2
            result = random.randint(1,sides)
            return await ctx.send(f"You rolled a `{result}` out of `{sides}`")
        except:
            return await ctx.send(f"{sides} is not a number")

    @roll_c.error
    async def roll_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send('Invalid die size')


    @commands.command(
        name = '8ball',
        aliases= ['8b','Eightball'],
        brief='It\'s a magic 8ball.',
        help="It's like 8ball, but sarcastic.",
        usage='8ball [question]'
        )
    async def sarcastic_eightball(self, ctx, *, question = None):
        if question == None:
            eightballembed = discord.Embed(
                title='Question:',
                description= 'Did I forget to ask a question?',
                colour=discord.Colour.blue()
                )
            eightballembed.add_field(name='🎱Answer:🎱', value='Yes. Yes you did.')
            return await ctx.send(embed=eightballembed)
        elif question.endswith('?'):
            eightballembed = discord.Embed(
                title='Question:',
                description= Format.discord(question),
                colour=discord.Colour.blue()
                )
            eightballembed.add_field(name='🎱Answer:🎱', value=f'{yesorno()}')
            return await ctx.send(embed=eightballembed)
        else:
            eightballembed = discord.Embed(
                title='Question:',
                description= f'{Format.discord(question)}?',
                colour=discord.Colour.blue()
                )
            eightballembed.add_field(name='🎱Answer:🎱', value=f'{yesorno()}')
            return await ctx.send(embed=eightballembed)


    @commands.command(
        name= 'Youtube',
        brief='Searches videos on youtube',
        aliases= ['YT', 'Search'],
        help='This will send a link containing the search text for a YouTube video.',
        usage='Youtube [search]',
        )
    async def search_on_youtube(self, ctx, *, searchtext = None):
        if searchtext != None:
            link = 'https://www.youtube.com/results?search_query='
            link += Format.youtube(searchtext)
            shortened = f'[Search Link]({link})'
            youtubeembed = discord.Embed(title='Youtube',description = shortened,color = discord.Colour.red())
            return await ctx.send(embed=youtubeembed)
        return await ctx.send("What the fuck do you wan't me to search?")

    @commands.command(
        name="Insult",
        brief="Insults someone",
        usage="insult <name> <second name> ...",
        help="Insults someone. It'll insult you if you don't tell it who."
        )
    @commands.cooldown(2, 5, type=commands.BucketType.member)
    async def insult_c(self, ctx, *, names=None):
        if names is None:
            return await ctx.send(self.insult.insult_me())
        names = names.replace("<", "%3C")
        names = names.replace(">", "%3E")
        names = names.split(" ")
        all = []
        for name in names:
            all.append(name)
        if len(all) == 1:
            insult = self.insult.insult_who(all[0])
        else:
            insult = self.insult.insult_many(all)

        insult = insult.replace("%3C", "<")
        insult = insult.replace("%3E", ">")
        embed = discord.Embed(title="Insult:", description=insult, color = Common_info.blue)
        embed.set_footer(text=ctx.author)
        return await ctx.send(embed=embed)

    @commands.group(hidden=True, name="tictactoe", aliases=['ttt'], )
    @commands.is_owner()
    async def tictactoe_start(self, ctx):
        return await ctx.send(self.tictac.make_board())

def setup(bot):
    bot.add_cog(Fun(bot))
