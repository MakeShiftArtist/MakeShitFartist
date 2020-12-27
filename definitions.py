import discord
import random
import asyncio
import requests
from random import randint
from datetime import datetime
import sqlite3 as sqlite
from trello import TrelloClient
import re


class Common_info:
    blue = 0x1E90FF
    red = 0xFF0000


class Trello:
    """Functions for trello"""
    class Info:
        def client(api_key, api_secret, token):
            return TrelloClient(
                api_key=api_key,
                api_secret=api_secret,
                token=token
            )

        def get_board(client, board_name):
            boards = client.list_boards()
            for board in boards:
                if board.name == board_name:
                    return board
            else:
                return None

        def get_list(board, list_name):
            lists = board.list_lists()
            for list in lists:
                if list.name == list_name:
                    return list
            else:
                return None

        def get_labels(board):
            labels = []
            for label in board.get_labels():
                if label is not None and label.color is not None:
                    labels.append(label)
            return labels

        def labels_with_names(base, labels_list):
            labels = []
            if labels_list == []:
                return []
            active_labels = Trello.Info.get_labels(base.board)
            for label in labels_list:
                for active_label in active_labels:
                    if active_label.color is None:
                        continue
                    elif active_label.name.lower() == label.lower():
                        labels.append(active_label)

            return list(set(labels))

    class Card_labels:
        def __init__(self, message=None):
            if message is None:
                message = "No title"
            label_pattern = "(?<=\[)\w+(?=\])"
            strip_pattern = "(\ )?\[\w+\](\ )?"
            labels = re.findall(label_pattern, message)
            if labels == []:
                labels = ['report']
            else:
                labels.append('report')

            self.labels = labels
            self.title = re.sub(strip_pattern, "", message)

    class Base:
        def __init__(self, client, board_name, list_name):
            self.client = client
            self.board = Trello.Info.get_board(client, board_name)
            self.list = Trello.Info.get_list(self.board, list_name)
            self.all_cards = self.list.list_cards()
            self.labels = Trello.Info.get_labels(self.board)

        def get_boards(self):
            return self.client.list_boards()

        def get_lists(self):
            return self.board.list_lists()

        def get_bugs(self):
            self.all_bugs = self.list.list_cards()
            return self.all_bugs

        def add_bug(self, message=None, desc=None, labels=[]):
            message = Trello.Card_labels(message)
            desc = desc if desc else 'No description'

            if labels is None:
                labels = ['report']
            card_labels = Trello.Info.labels_with_names(self, labels)

            card = self.list.add_card(
                message.title, desc, position='top', labels=card_labels
            )
            self.all_cards = self.list.list_cards()
            return card


"""
Random functions
"""


def insult() -> str:
    insultname = [
                'you baboon', 'dumbass', 'cretin', 'retard', 'loser',
                'idiot', 'bitch baby', 'redditard', 'skibtard', 'fuckwit',
                'asshat', 'dimwit', 'numb nuts', 'pissbaby', 'walnut',
                'troglodyte', 'cave brains', 'mongoloid', 'neanderthal',
                'smooth brain', 'mouth breather', 'moron', 'window licker',
                'whore', 'simpleton', 'buffoon', 'bird brain',
                'toe licker', 'stove toucher', 'dipshit', 'fuck nuts',
                'baby nuts', 'shit stain', 'douchebag']
    total = len(insultname)-1
    name = insultname[random.randint(0, total)]
    return name


def yesorno() -> str:
    eightballresponses = [
        "As far as I can tell. But what do I know? I'm just a shitty bot.",
        "Ask again later, because idgaf rn.",
        "Ooo I could tell you... but nah lol.",
        "I'm gonna keep it 💯 with you chief... I have no fucking idea. Lol",
        "Really? That's the best question you could come up with?",
        "Don’t count on it. Who am I kidding? You couldn't count to 1 if you tried lol.",
        "Yes, according to this random reponse lol",
        "According to my calculations... Uhhh sure.",
        "I'd argue yes if this wasn't preprogrammed.",
        "No. No I don't think so. Lol jk bots can't think.\n\n\nyet...",
        "My sources say no.\n**Source:** Dude, trust me.",
        "Kind of a stupid question don't you think?",
        "I'm at least 40% positive that the answer is yes.",
        "I'm high af rn idk.",
        "Signs point to yes. Wait that says no. No, I was right originally. Wait. Fuck, I wish I could read.",
        "I doubt that more than I doubt myself.",
        "Does it matter? I assume if you're asking a discord bot, that it's likely not very important.",
        "Yes. Now stop asking me stupid questions ffs.",
        "Send me toe pics and I'll say whatever you want me to",
        "Sure, why tf not?"
    ]
    total8ball = len(eightballresponses)-1
    return eightballresponses[random.randint(0, total8ball)]


class Format:

    @staticmethod
    def multiple(names: list) -> str:
        res = ""
        if len(names) == 1:
            return names[0]

        for name in names:
            if name == names[-1]:
                res += "and " + name
            elif name == names[-2]:
                res += name + " "
            else:
                res += name + ", "
        return res

    @staticmethod
    def no_spaces(string) -> str:
        return string.replace(' ', '')

    @staticmethod
    def no_double_spaces(string):
        string = str(string)
        space = "  "
        for space in string:
            string = string.replace('  ', ' ')
        return string

    @staticmethod
    def not_nothing(string: str) -> str:
        """Doesn't allow and empty str"""
        if string == '':
            return '"Fuck You"'
        else:
            return string

    @staticmethod
    def prefix(string) -> str:
        string = Format.discord(string)
        string = Format.no_spaces(string)
        string = Format.not_nothing(string)
        return string

    @staticmethod
    def trello_description(fields: list = None) -> str:
        if fields is None:
            return 'No description given'
        if len(fields) >= 2:
            return '\n'.join(fields[1:])
        elif len(fields) == 1:
            return 'No description given'

    @staticmethod
    def discord(string) -> str:
        string = str(string)
        doublespace = '  '
        string = string.replace('\n', ' ')
        for doublespace in string:
            string = string.replace('  ', ' ')
        return string

    @staticmethod
    def youtube(string) -> str:
        string = string.replace('%', '%25')
        string = string.replace('+', '%2B')
        string = string.replace(' ', '+')
        string = string.replace('\\', '%5C')
        string = string.replace('/', '%2F')
        string = string.replace('*', '%2A')
        string = string.replace('=', '%3D')
        string = string.replace('(', '%28')
        string = string.replace(')', '%29')
        string = string.replace('&', '%26')
        string = string.replace('^', '%5E')
        string = string.replace('$', '%24')
        string = string.replace('#', '%23')
        string = string.replace('@', '%40')
        string = string.replace('!', '%21')
        string = string.replace('`', '%60')
        string = string.replace('}', '%7d')
        string = string.replace('{', '%7B')
        string = string.replace('[', '%5B')
        string = string.replace(']', '%5D')
        string = string.replace('|', '%5C')
        string = string.replace('?', '%3F')
        string = string.replace(',', '%2C')
        string = string.replace('\'', '%27')
        string = string.replace(':', '%3A')
        string = string.replace(';', '%3B')
        string = string.replace('<', '%3C')
        string = string.replace('>', '%3E')
        return string


class Embeds:
    @staticmethod
    def ip_embed(info):
        embed = discord.Embed(
            title='IP Info',
            description=f"> ISP: {info.isp}",
            color=Common_info.blue
            )

        embed.add_field(name='Country', value=f"> {info.country}", inline=False)
        embed.add_field(name='State', value=f"> {info.state}", inline=False)
        embed.add_field(name='City', value=f"> {info.city}", inline=False)
        embed.add_field(name='Zipcode', value=f"> {info.zip}", inline=False)
        if info.mobile:
            embed.add_field(
                name='This is likely a mobile device',
                value='> The location data for this IP is likely wrong',
                inline=False
                )
        if info.proxy:
            embed.add_field(
                name='This is likely a proxy IP',
                value='> This likely isn\'t their actual IP',
                inline=False
                )
        embed.set_footer(text=info.ip)
        return embed

    @staticmethod
    def trello_embed(base):
        all_labels = Trello.Info.get_labels(base.board)
        valid_labels = ''
        for item in all_labels:
            if item == all_labels[-1]:
                valid_labels += f"`[{item.name}]`"
            else:
                valid_labels += f"`[{item.name}]` | "

        link = 'https://trello.com/b/6VnXOnCr/imonke-development'
        desc = f'> You can find the board [here]{link}). '
        desc += 'You must be in iMonke to use this command. '
        desc += 'Spamming or abusing this will get you blacklisted.'
        embed = discord.Embed(
            title="iMonke Trello Board",
            description=desc,
            color=Common_info.blue)

        embed.add_field(
            name='Usage',
            value='`-trello <labels> [title]\n<description>`',
            inline=False
            )

        example = '> -trello [frontend] [bug] Image rendering\n'
        example += '> When feed scrolling, sometimes images will not render.'
        embed.add_field(
            name='Example',
            value=example,
            inline=False)

        usage = "> The brackets `[]` around the labels are required."
        usage += '\n> `<label>` WILL NOT WORK! It must be `[label]`'
        embed.add_field(
            name='Label Tips',
            value=usage,
            inline=False
            )

        embed.add_field(
            name='Valid Labels',
            value=valid_labels,
            inline=False
            )

        embed.add_field(
            name='How to add a description',
            value='To add a description, create a new line',
            inline=False
            )
        return embed

    @staticmethod
    def loading(title="Loading..."):
        title = f'<a:loading:774385294106689557> {title}'
        return discord.Embed(title=title, color=Common_info.blue)

    @staticmethod
    def moderation_success(ctx, user, command='Command', reason=None) -> discord.Embed:
        title = f'\U00002705 {command} successful'
        if reason is None:
            reason = f'**Mod:** {ctx.author} (**ID:** {ctx.author.id}): No reason given'
        return discord.Embed(
            title=title,
            description=reason,
            color=Common_info.blue
            )

    @staticmethod
    def custom_error(title: str, suggestion: str) -> discord.Embed:
        title = '\U0000274c ' + title
        return discord.Embed(
            title=title,
            description=suggestion,
            color=Common_info.red
            )

    @staticmethod
    def error_embed(ctx, error, commands) -> discord.Embed:
        if isinstance(error, commands.CommandOnCooldown):
            time = round(error.retry_after*100)/100
            title = 'Command On Cooldown'
            reason = f'Slow down, {insult()}.\nTry again in {time} seconds.'

        elif isinstance(error, discord.NotFound):
            title = "404 Not Found"
            reason = error.original.text

        elif isinstance(error, commands.NoPrivateMessage):
            title = 'Server Only'
            reason = f'You can only use this command in servers, {insult()}.'

        elif isinstance(error, commands.BotMissingPermissions):
            title = 'Bot Missing Permissions'
            reason = f'I don\'t have perms for that, {insult()}.'

        elif isinstance(error, commands.MissingPermissions):
            title = 'Missing Permissions'
            reason = f'Lol try again when you have perms, {insult()}.'

        elif isinstance(error, commands.BadArgument):
            title = "Bad Argument"
            reason = f'Try using the help command, {insult()}.'

        elif isinstance(error, commands.MissingRequiredArgument):
            title = "Missing Required Argument"
            reason = f"Think you might be missing an argument, {insult()}?"
        else:
            return None
        return discord.Embed(
            title='\U0000274c ' + title,
            description=reason,
            color=Common_info.red)

    @staticmethod
    def unknown_error_embed(ctx, error) -> discord.Embed:
        embed = discord.Embed(
            title=f'\U0000274c {ctx.command} failed.',
            description='An unknown error occurred.',
            color=Common_info.red)
        try:
            desc = error.original
        except AttributeError:
            desc = error
        embed.add_field(name='Error:', value=str(desc), inline=False)
        return embed

    @staticmethod
    def error_log(ctx, error, command=None) -> discord.Embed:
        # Basic info
        guild = ctx.message.guild
        author = ctx.message.author
        if guild:
            where = guild.name
        else:
            where = "DMs"
        if command is None:
            command = "Command"

        # Final info
        location_data = f"{command} raised an exception in {where} by {author}."
        now = Datetime._now()
        time = Datetime.get_full_date(now)

        # Terminal
        eql = "="*20
        print(eql)
        print(location_data)
        print(f"Type: {type(error)}\n")
        print(f"Full error: {str(error)}\n")
        print(f"Time: {time}\n")
        print(eql + '\n')

        # Embed
        embed = discord.Embed(
            title=f'\U0000274c {command} failed',
            description='An unknown error occurred',
            color=Common_info.red)
        embed.add_field(name='Where:', value=location_data, inline=False)
        embed.add_field(name='Type:', value=type(error), inline=False)
        embed.add_field(name='Full Error:', value=str(error), inline=False)
        embed.add_field(name="Time:", value=time, inline=False)
        return embed

    @staticmethod
    def error_handler(ctx, error, commands, command=None):
        embed = Embeds.error_embed(ctx, error, commands)
        log_embed = None
        if embed is None:
            embed = Embeds.unknown_error_embed(ctx, error)
            log_embed = Embeds.error_log(ctx, error, command)
        return [embed, log_embed]

    @staticmethod
    def user_info(ctx, member):
        full_name = str(member.name) + '#' + str(member.discriminator)
        registered_date = Datetime.get_full_date(member.created_at)

        embed = discord.Embed(
            title=member.display_name,
            description=full_name,
            scolor=Common_info.blue
            )

        embed.add_field(
            name='Created on',
            value=registered_date,
            inline=False
            )
        try:
            join_date = Datetime.get_full_date(member.joined_at)
            embed.add_field(
                name='Joined on',
                value=join_date,
                inline=False
                )
        except AttributeError:
            pass

        try:
            activity = member.activity
        except AttributeError:
            activity = None
        if activity is not None:
            activity = str(activity.name)
            try:
                emoji = activity.emoji
                if emoji is not None:
                    activity = str(emoji) + " " + activity
            except AttributeError:
                pass
            embed.add_field(
                name='Activity',
                value=activity,
                inline=False)

        if ctx.guild is not None:
            if member in ctx.guild.members:
                if not member.top_role.is_default():
                    embed.add_field(
                        name='Top Role',
                        value=member.top_role.mention,
                        inline=False
                    )
                roles = member.roles[1:-1]
                if roles != []:
                    allroles = ''
                    for i in roles:
                        allroles += '{} '.format(i.mention)
                    embed.add_field(name='All Roles', value=allroles)

        embed.set_image(url=member.avatar_url)
        embed.set_footer(text=f'ID: {member.id}')
        return embed


class Numbers:
    """
    Misc functions
    """
    @staticmethod
    def ordinal(num):
        n = int(num)
        if 4 <= n <= 20:
            suffix = 'th'
        elif n == 1 or (n % 10) == 1:
            suffix = 'st'
        elif n == 2 or (n % 10) == 2:
            suffix = 'nd'
        elif n == 3 or (n % 10) == 3:
            suffix = 'rd'
        elif n < 100:
            suffix = 'th'
        ord_num = str(n) + suffix
        return ord_num

    @staticmethod
    def str_num(*nums):
        strings = []
        if len(nums) == 1:
            string = "{:,.2f}".format(nums[0])
            return string[:-3]
        for num in nums:
            string = "{:,.2f}".format(num)
            strings.append(string[:-3])
        return strings


class Datetime:
    """Date functions as strings/names"""

    @staticmethod
    def now():
        return datetime.now()

    @staticmethod
    def _time_common(time=None):
        if time is None:
            time = datetime.now()
        return time.strftime('%H:%M %p')

    @staticmethod
    def get_full_date(time=None):
        if time is None:
            time = datetime.now()
        start = time.strftime('%A, %B')
        day = Numbers.ordinal(int(time.strftime('%d')))
        end = time.strftime('%Y %H:%M %p')
        return f"{start} {day}, {end}"


class Database:
    def __init__(self, file):
        self.database = sqlite.connect(file)
        self.cursor = self.database.cursor()
        self.db = self.database
        self.start()

    def get_passcode(self):
        return str(randint(100001, 999999))

    def start(self):
        cursor = self.cursor
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            DiscordID TINYTEXT,
            iFunnyID TINYTEXT
            )
            """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Passcodes (
            DiscordID TINYTEXT,
            iFunnyID TINYTEXT,
            Password TINYTEXT
            )
            """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS GuildPrefixes (
            GuildID TINYTEXT,
            Prefix TINYTEXT
            )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Mutes (
            GuildID TINYTEXT,
            MemberID TINYTEXT,
            IsMuted BOOL
            )
            """)


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Autoposts (
                MemberID INT,
                Total INT
            )
        """)

    def save(self):
        self.db.commit()

    def close(self):
        self.database.commit()
        self.cursor.close()
        self.db.close()

    def get_select(self, select_statement, *args):
        variable = "{}"
        for arg in args:
            select_statement = select_statement.replace(
                "{}", str(arg)
                )
        self.cursor.execute(select_statement)
        item = self.cursor.fetchone()
        if item is not None:
            if len(item) == 1:
                return item[0]
            else:
                return item
        else:
            return None


class iFunny:
    """IFunny Specific Embeds/Functions"""

    @staticmethod
    def getrankdays(rank: str, days: int):
        milestones = {
            'Meme explorer': 5, 'Meme bro': 25, 'Meme daddy': 50,
            'Dank memer': 100, 'Meme master baker': 200,
            'Deep fried memer': 300, 'Saucy memer': 500,
            'Original Meme Gangster': 666, 'Meme demon': 911,
            'Steal beams of memes': 1000, 'Meme dealer': 1500,
            'iFunny Veteran': 2000, "Chef's meme agent": 3000
        }
        if rank in milestones:
            days = milestones[rank] - days
            return days
        else:
            return 0

    @staticmethod
    def iFunnyUserEmbed(user):
        username = str(user.nick)
        nextdays = iFunny.getrankdays(str(user.rank), int(user.days))
        if user.is_verified:
            username += ' <:ifunnyverified:768264154628096060>'

        featemoji = '<:ifunnydislike:768264184441864233>'
        smilemoji = '<:ifunnylike:768264195174563910>'

        if user.feature_count != 0:
            featemoji = '<:ifunnyfeatured:768264176661430282>'
        stats = Numbers.str_num(
            user.days, nextdays, user.feature_count,
            user.post_count, user.smiles_count,
            user.subscriber_count, user.subscription_count
            )

        ifunnyembed = discord.Embed(
            title=username,
            description=user.about,
            color=Common_info.blue
            )

        ifunnyembed.add_field(
            name=user.rank,
            value=f'> `{stats[0]}` Days\n> `{stats[1]}` Next',
            inline=False
            )

        post_stats = f'> `{stats[3]}` Posts\n> `{stats[4]}` Smiles {smilemoji}'
        ifunnyembed.add_field(
            name='Posts',
            value=f'> `{stats[2]}` Features {featemoji}\n{post_stats}',
            inline=True
            )

        ifunnyembed.add_field(
            name='Sub Stats',
            value=f'> `{stats[5]}` Subs\n> `{stats[6]}` Subbed'
            )
        ifunnyembed.add_field(
            name='Profile',
            value=f'[Visit](https://ifunny.co/user/{user.nick})',
            inline=False
            )

        if (user.profile_image):
            ifunnyembed.set_thumbnail(url=user.profile_image.url)
        else:
            url = 'https://cdn.discordapp.com/attachments/76827135814834588'
            ifunnyembed.set_thumbnail(
                url=f'{url}/779123930672922644/1605828002100.png')

        if (user.cover_image):
            ifunnyembed.set_image(url=user.cover_image.url)
        else:
            url = 'https://www.divinewings.co.in/admin/images/pageBanner'
            ifunnyembed.set_image(url=f'{url}/default/default-banner.jpg')

        ifunnyembed.set_footer(text=f'ID: {user.id}')

        return ifunnyembed

    @staticmethod
    def iFunnySubEmbed(user, robot):
        if user.is_subscription:
            subbedto = 'Unsubscribed to {}'.format(user.nick)
            embed = discord.Embed(
                title=subbedto,
                description='Use `-sub` to sub',
                color=Common_info.blue
                )
            embed.set_footer(text=robot.nick)
            return embed
        else:
            subbedto = 'Subscribed to {}'.format(user.nick)
            embed = discord.Embed(
                title=subbedto,
                description='Use `-sub` to unsub',
                color=Common_info.blue)
            embed.set_footer(text=robot.nick)
            return embed


class Autopost:
    def __init__(self, client, subreddit):
        self.running = False
        self.bot = client
        self.subreddit = subreddit

    async def get_meme(self):
        for post in self.subreddit.new(limit=10):
            if post.stickied:
                continue
            return post.url

    async def post_meme(self, meme_url):
        meme = self.bot.post_image_url(
            image_url=meme_url,
            visibility='public',
            wait=False,
            timeout=60,
            schedule=None
            )
        return meme

    async def start(self):
        self.running = True
        while self.running:
            meme_url = await self.get_meme(self.subreddit)
            await self.post_meme(self.bot, meme_url)
            wait = random.randint(1, 20)
            asyncio.sleep(wait*60)

    async def stop(self):
        if self.running:
            self.running = False


class IPInfo:
    """ Base IP Info Class """

    def __init__(self, ip_address=None):
        self.api = 'http://ip-api.com/json/'
        self.ip = ip_address
        self.ip_address = self.ip
        self.json = self.get()

    def get(self) -> dict:
        fields = {"fields": "35382269"}
        site = requests.get(f'{self.api}{self.ip}', params=fields)
        if not site.ok:
            raise Exception(f"404 Error: {site.text}")
        json = site.json()
        self.json = json
        return json

    def is_success(self) -> bool:
        json = self.json
        if json == {}:
            return False
        status = json['status']
        if status == 'success':
            return True
        else:
            return False

    def ip_info(self):
        return self.get_ip_info(self.json)

    def error(self):
        return self.get_error(self.json)

    class get_ip_info:
        """ Gets all the data for the IP """

        def __init__(self, json):
            self.ip = json['query']
            self.is_proxy = json['proxy']
            self.proxy = self.is_proxy
            self.isp = json['isp']
            self.continent = json['continent']
            self.country = json['country']
            self.state = json['regionName']
            self.state_short = json['region']
            self.city = json['city']
            self.district = json['district']
            self.zipcode = json['zip']
            self.zip = self.zipcode
            self.latitude = json['lat']
            self.lat = self.latitude
            self.longitude = json['lon']
            self.lon = self.longitude
            self.timezone = json['timezone']
            self.coords = [self.lat, self.lon]
            self.mobile = json['mobile']

    class get_error:
        def __init__(self, json):
            self.error = json['message']
            self.query = json['query']
            self.ip = self.query
            self.message = f"Error: {self.error}\nQuery: {self.query}"


class Insults:

    def __init__(self):
        self.api = "https://insult.mattbas.org/api/en/insult.json"
        self.insult_names = [
            'you baboon', 'dumbass', 'cretin', 'retard', 'loser',
            'idiot', 'bitch baby', 'redditard', 'skibtard', 'fuckwit',
            'asshat', 'dimwit', 'numb nuts', 'pissbaby', 'walnut',
            'troglodyte', 'cave brains', 'mongoloid', 'neanderthal',
            'smooth brain', 'mouth breather', 'moron', 'window licker',
            'whore', 'simpleton', 'buffoon', 'bird brain',
            'toe licker', 'stove toucher', 'dipshit', 'fuck nuts',
            'baby nuts', 'shit stain', 'douchebag']
        self.len = len(self.insult_names)-1

    def insult(self):
        i = random.randint(0, self.len)
        return self.insult_names[i]

    def insult_me(self):
        r = requests.get(self.api)
        json = r.json()
        if r.ok:
            return json['insult']
        else:
            raise Exception(json["error_message"])

    def insult_who(self, name=None):
        if name is None:
            raise Exception("You need a name to insult")
        q = {"who": name}
        r = requests.get(self.api, params=q)
        json = r.json()
        if r.ok:
            return json["insult"]
        else:
            raise Exception(json["error_message"])

    def insult_many(self, names: list = None):
        if names is None:
            raise Exception("You need a list of names to insult")
        name_str = Format.multiple(names)
        q = {"who": name_str, "plural": "on"}
        r = requests.get(self.api, params=q)
        json = r.json()
        if r.ok:
            return json["insult"]
        else:
            raise json["error_message"]
