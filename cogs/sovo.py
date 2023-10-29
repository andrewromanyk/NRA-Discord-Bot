import nextcord
from nextcord.ext import commands, tasks
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import sqlite3, json
import datetime, pytz
from songvote import *

RATING_IN_PROCESS = True
#a very scary thing to turn local time to UTC
#change timezone to whichever you need
timezone = pytz.timezone('Europe/Kyiv')
timenow = datetime.datetime.now(timezone)
TIME_FOR_LOOP = timezone.localize(datetime.datetime(year=timenow.year, month=timenow.month, day=timenow.day, hour=20, minute=00), is_dst=True).astimezone(pytz.utc).time()

async def canVote(interaction: nextcord.Interaction):  
    global RATING_IN_PROCESS
    if not RATING_IN_PROCESS:
        embed_decline = nextcord.Embed(title="Прямо зараз неможливо виконати команду\nМожливо виводяться результати голосування", color=nextcord.Color.blurple())
        await interaction.send(embed=embed_decline, ephemeral=True)
        return False
    return True

async def forAdmin(interaction: nextcord.Interaction):
    if not interaction.permissions.administrator:
        embed_notadmin = nextcord.Embed(title=f"Ви не можете використати цю команду\nНеобхідні права адміністратора", color=nextcord.Color.blurple())
        await interaction.send(embed=embed_notadmin, ephemeral=True)
        return False
    return True

async def songlist_global(bot: commands.bot):
    with open("channels.json") as channels:
        channel = json.loads(channels.read())
    channel_id = channel["voteresults"]

    description = getsonglist()

    embed_songlist_first = nextcord.Embed(title="Новий день, нове голосування!", color=nextcord.Color.green())
    message = await bot.get_channel(channel_id).send(embed=embed_songlist_first)

    embed_songlist = nextcord.Embed(title="Список усіх пісень:", description=description, color=nextcord.Color.blurple())
    message = await bot.get_channel(channel_id).send(embed=embed_songlist)
    message_id = message.id

    with open("channels.json") as channels:
        text = json.load(channels)
    text["songlist_message"] = message_id
    with open("channels.json", "w") as channels:
        json.dump(text, channels, indent=2)
    

def getsonglist():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    cursor.execute(f"""SELECT name, author, link FROM musicLinks""")
    songlist = cursor.fetchall()

    description = ""
    for song in songlist: description += f"{song[1]} - {song[0]}\n{song[2]}\n\n"

    conn.close()

    return description

class SongVote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.showresult.start()
        self.changelistmessage.start()

    def cog_unload(self):
        self.showresult.cancel()
        self.changelistmessage.cancel()
        

    #Used to show result of the vote
    @tasks.loop(time = TIME_FOR_LOOP)
    async def showresult(self):
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, author, time, link, votes FROM musicLinks ORDER BY votes DESC")
        rating = cursor.fetchall()
        text = ""
        for i in range(len(rating)):
            text += f"**{i}. {rating[i][0]+'  --  '+str(rating[i][4])}**{rating[i][1]} | {rating[i][2]} \n{rating[i][3]}\n\n"

        if len(rating) < 1: text = "Не було запропоновано жодної пісні :("

        cursor.execute("DELETE FROM musicLinks")
        cursor.execute("DELETE FROM voted")
        embed_decline = nextcord.Embed(title="Голосування завершено!\nРезультати:", description=text, color=nextcord.Color.blurple())
        embed_decline.set_thumbnail("https://i.pinimg.com/originals/10/bd/23/10bd2392da16e33ab81c8a9862c3e116.gif")
        with open("channels.json") as channels:
            channel = json.loads(channels.read())
        channel_id = channel["voteresults"]

        await self.bot.get_channel(channel_id).send(embed=embed_decline)
        conn.commit()
        conn.close()

        await songlist_global(self.bot)
    
    @tasks.loop(seconds = 30)
    async def changelistmessage(self):
        print("edited message")
        with open("channels.json") as channels:
            text = json.load(channels)
        message_id = text["songlist_message"]
        channel_id = text["voteresults"]

        description = getsonglist()

        embed_songlist = nextcord.Embed(title="Список усіх пісень:", description=description, color=nextcord.Color.blurple())

        message = await self.bot.get_channel(channel_id).fetch_message(message_id)

        await message.edit(embed = embed_songlist)


    @showresult.before_loop
    async def before_printer(self):
        print('waiting for show result')
        await self.bot.wait_until_ready()

    @changelistmessage.before_loop
    async def before_printer(self):
        print('waiting for changelistmessage')
        await self.bot.wait_until_ready()

    #Allow users to offer songs for the vote
    #Anyone can offer
    @nextcord.slash_command(name="offersong", description="запропонувати пісню для рейтингу")
    async def offersong(self, interaction: nextcord.Interaction,
        song_link: str = nextcord.SlashOption(
            name = "link",
            required=True
        )):

        if not await canVote(interaction): return

        await interaction.response.defer()

        #Check if it is a valid link
        val = URLValidator()
        try: 
            val(song_link)
        except ValidationError: 
            embed_notlink = nextcord.Embed(title="Аргумент не є посиланням", color=nextcord.Color.blurple())
            await interaction.send(embed=embed_notlink, ephemeral=True)
            return
        
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()

        cursor.execute("""SELECT id FROM musicLinks""")
        usersIds = cursor.fetchall()
        userId = interaction.user.id

        songname = ""

        if (str(userId),) in usersIds:
            cursor.execute(f"""SELECT name FROM musicLinks WHERE id == {str(userId)}""")
            songname = cursor.fetchone()[0]

            embed = nextcord.Embed(description=f"Пісня, яку Ви додали до цього: {songname}\n\nБажаєте замінити її, чи залишити стару?\nОбмежень на кількість змін пісень немає", title="Ви вже запропонували одну пісню", color=nextcord.Color.blurple())
            button = sv_buttons.replaceSong()
            answer = await interaction.send(embed=embed, ephemeral=True, view = button)
            await button.wait()
            await answer.delete()

            if not button.value:
                embed_decline = nextcord.Embed(title="Зміну було відмінено", color=nextcord.Color.blurple())
                await interaction.send(embed=embed_decline, ephemeral=True)
                return

        attributes = sv_songattr.getSongAttr(song_link)

        if attributes[0] == "":
            embed_badlink = nextcord.Embed(title="Посилання пошкоджене, або виникла помилка,\nчерез яку неможливо ідентифікувати пісню", color=nextcord.Color.blurple())
            await interaction.send(embed=embed_badlink, ephemeral=True)
            return
        elif attributes[0] == "nosource":
            embed_badlink = nextcord.Embed(title="Цей сервіс не підтримується.\nПідтримуються YouTube Music, YouTube, Spotify", color=nextcord.Color.blurple())
            await interaction.send(embed=embed_badlink, ephemeral=True)
            return
        
        cursor.execute(f"""DELETE FROM musicLinks WHERE id = '{userId}'""")
        cursor.execute(f"""DELETE FROM voted WHERE name = '{songname}'""")
        cursor.execute("""INSERT INTO musicLinks VALUES(?, ?, ?, ?,  ?, ?)""", (userId, song_link, *attributes, 0))
        conn.commit()
        embed_added = nextcord.Embed(title=f"Успішно додано пісню {attributes[0]} до списку пісень", color=nextcord.Color.blurple())
        await interaction.send(embed=embed_added, ephemeral=True)


    #Prints out the songs offered
    #Can be used by all users
    @nextcord.slash_command(name="songlist", description="список пісень")
    async def songlist(self, interaction: nextcord.Interaction):
        await interaction.response.defer()

        if not await canVote(interaction): return

        description = getsonglist()

        embed_songlist = nextcord.Embed(title="Список усіх пісень:", description=description, color=nextcord.Color.blurple())
        await interaction.send(embed=embed_songlist, ephemeral=True)


    #Allows users to vote for songs
    #Can be used by all users
    @nextcord.slash_command(name="votesong", description="список пісень")
    async def votesong(self, interaction: nextcord.Interaction):
        await interaction.response.defer()

        if not await canVote(interaction): return

        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()

        id = interaction.user.id

        if cursor.execute(F"""SELECT EXISTS(SELECT id FROM voted WHERE id='{str(id)}')""").fetchone() == (1,):
            
            button = sv_buttons.replaceSong()
            votedsong = cursor.execute(f"""SELECT name FROM voted WHERE id = {id}""").fetchone()[0]
            embed_alreadyvoted = nextcord.Embed(title=f'Ви уже голосували за {votedsong}\nБажаєте змінити голос?', color=nextcord.Color.blurple())
            await interaction.send(embed=embed_alreadyvoted, ephemeral=True, view=button)
            await button.wait()

            if not button.value:  
                embed_votend = nextcord.Embed(title="Голосування відмінено", color=nextcord.Color.blurple())
                await interaction.send(embed=embed_votend, ephemeral=True)
                return
            
            cursor.execute(f"""DELETE FROM voted WHERE id = '{id}'""")
            cursor.execute("""UPDATE musicLinks SET votes = votes - 1 WHERE name = ?""", (votedsong, ))
        conn.commit()
        conn.close()

        view = sv_dropdown.dropdownView()
        embed_voted = nextcord.Embed(title=f"Оберіть пісню, за яку хочете проголосувати", color=nextcord.Color.blurple())
        await interaction.send(embed=embed_voted, ephemeral=True, view=view)

    #Shows result of the vote
    #Can be called at any time. Only for users with "administrator" permission
    @nextcord.slash_command(name="voteresult", description="викликати результат голосуванння")
    async def voteresult(self, interaction: nextcord.Interaction):
        if not await forAdmin(interaction) or not await canVote(interaction): return

        global RATING_IN_PROCESS
        RATING_IN_PROCESS = False
        await interaction.response.defer()
        await self.showresult()
        RATING_IN_PROCESS = True