from minesweeper import draw
import discord
import asyncio
from discord.ext import commands
from definitions import *
from ifunny import objects
import random
import praw
import re


ClientBase = objects._mixin.ClientBase()

class fun(commands.Cog, name='Fun'):
    '''Commands to add some fun to your server'''
    def __init__(self, bot):
        self.bot = bot
        self.insult = Insults()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Fun Cog loaded')


    @commands.command(name='Minesweeper', brief='Sends a minesweeper game', help='Sends a game of Minesweeper using spoilers.',
    aliases=['MS', 'Minespoiler'],usage='Minesweeper <size> <bombs>')
    async def minesweeper_c(self, ctx, size=8, bombs=8):
        if size < 2:
            size = 2
        if size > 13:
            size = 13
        if bombs >= (size * size) - 1:
            bombs = (size * size) - 1
        board = draw(size, size, bombs)
        await ctx.send(f'**Minesweeper: {size} by {size} with {bombs} total bombs.\n{board}**')


    @minesweeper_c.error
    async def minesweeper_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send('That\'s not a number you baboon')

    @commands.command(name='Bubblewrap',brief='Sends bubble wrap',aliases=['Pop', 'Bubble'],
    help='This will send bubble wrap ising spoilers.\n> Pretty simple really.',usage='Bubblewrap <amount>')
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


    @commands.command(name='Roll',brief='Rolls a die', usage='Roll <sides>',
    help='Will give you a random number and whatever you input.')
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


    @commands.command(name = '8ball', aliases= ['8b','Eightball'],brief='It\'s a magic 8ball.',
    help="It's like 8ball, but sarcastic.", usage='8ball [question]')
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


    @commands.command(name= 'Youtube', brief='Searches videos on youtube', aliases= ['YT', 'Search'],
    help='This will send a link containing the search text for a YouTube video.', usage='Youtube [search]')
    async def search_on_youtube(self, ctx, *, searchtext = None):
        if searchtext != None:
            link = 'https://www.youtube.com/results?search_query='
            link += Format.youtube(searchtext)
            shortened = f'[Search Link]({link})'
            youtubeembed = discord.Embed(title='Youtube',description = shortened,color = discord.Colour.red())
            return await ctx.send(embed=youtubeembed)
        return await ctx.send("What the fuck do you wan't me to search?")

    @commands.command(name="Insult", brief="Insults someone", usage="insult <name> <second name> ...",
    help="Insults someone. It'll insult you if you don't tell it who.")
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



def setup(bot):
    bot.add_cog(fun(bot))
