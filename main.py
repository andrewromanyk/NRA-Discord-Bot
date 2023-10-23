import nextcord
from nextcord.ext import commands
import datetime
import random
import re
import sqlite3
from key import KEY
from songvote import *
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

image_url = "https://media.istockphoto.com/id/524712856/pl/wektor/stos-monet-ilustracja-wektorowa-ikony-p%C5%82aski-stos-pieni%C4%99dzy-pojedyncze.jpg?s=612x612&w=0&k=20&c=YnHQaj83pN7DpeP6AY5jiIVpFVh3is9LKr3b-h5z-TM="

BOT_KEY = KEY

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="l.", intents=intents)

@bot.event
async def on_ready():
    print(f"Started working at {datetime.datetime.utcnow()}")

@bot.slash_command(name="addrole", description="тестовий створення ролі")
async def addrole(interaction: nextcord.Interaction,
    role_name: str = nextcord.SlashOption(
        name = "role_name",
        required=True
    ),
        user: nextcord.Member = nextcord.SlashOption(
        name = "user",
        description="учасник, якому надається роль",
        autocomplete=True,
        required=True
    ),
    rgb: str = nextcord.SlashOption(
        name = "rgb",
        description="rgb колір ролі",
        #default=" ".join([str(random.randint(0, 255)) for i in range(3)]),
        required=False
    )):

    if rgb == None:
        #default value would return the same numbers every time, so this part is needed.
        random.seed = datetime.time
        rgb = " ".join([str(random.randint(0, 255)) for i in range(3)])

    try:
        #Turning the color option to usable form
        rgb_list = [int(i) for i in re.split(',|\.| ', rgb)[:3]]
    except ValueError:
        #If the color was sent in the wrong format or wrong values were delivered
        await interaction.send("Неправильне введення RGB значення. Правильний формат: '255 255 255'", ephemeral=True)
    #logging
    print(f"{interaction.user} used command {bot.slash_command.__name__}")

    role = await interaction.guild.create_role(name=role_name, color=nextcord.Color.from_rgb(*rgb_list))
    await user.add_roles(role)

    await interaction.send(f"You created a role '{role.name}' for {user.mention}", ephemeral=True)

    print(f"Created role named {role_name} and colored {rgb_list}")

@bot.slash_command(name="offersong", description="запропонувати пісню для рейтингу")
async def offersong(interaction: nextcord.Interaction,
    song_link: str = nextcord.SlashOption(
        name = "link",
        required=True
    )):

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

    try:
        cursor.execute("""CREATE TABLE musicLinks (
                id TEXT,
                link TEXT,
                name TEXT,
                author TEXT,
                time TEXT,
                votes INTEGER
        )""")
    except: pass

    cursor.execute("""SELECT id FROM musicLinks""")
    usersIds = cursor.fetchall()
    print(usersIds)

    userId = interaction.user.id
    print(userId)

    if (str(userId),) in usersIds:
        cursor.execute(f"""SELECT name FROM musicLinks WHERE id == {str(userId)}""")
        songname = cursor.fetchone()[0]
        embed = nextcord.Embed(description=f"Пісня, яку Ви додали до цього: {songname}\n\nБажаєте замінити її, чи залишити стару?\nОбмежень на кількість змін пісень немає", title="Ви вже запропонували одну пісню", color=nextcord.Color.blurple())
        button = buttons.replaceSong()
        answer = await interaction.send(embed=embed, ephemeral=True, view = button)
        await button.wait()
        await answer.delete()
        if button.value:
            attributes = songattr.getSongAttr(song_link)
            if attributes[0] == "":
                embed_badlink = nextcord.Embed(title="Посилання пошкоджене, або виникла помилка,\nчерез яку неможливо ідентифікувати пісню", color=nextcord.Color.blurple())
                await interaction.send(embed=embed_badlink, ephemeral=True)
                return
            cursor.execute(f"""UPDATE musicLinks SET id = ?, link = ?, name = ?, author = ?, time = ?, votes = ? WHERE id = {userId}""", (userId, song_link, *attributes, 0))
            conn.commit()
            embed_accept = nextcord.Embed(title=f"Успішно замінив пісню на {attributes[0]}", color=nextcord.Color.blurple())
            await interaction.send(embed=embed_accept, ephemeral=True)
            return
        else:
            embed_decline = nextcord.Embed(title="Зміну було відмінено", color=nextcord.Color.blurple())
            await interaction.send(embed=embed_decline, ephemeral=True)

    else:
        attributes = songattr.getSongAttr(song_link)
        if attributes[0] == "":
                embed_badlink = nextcord.Embed(title="Посилання пошкоджене, або виникла помилка,\nчерез яку неможливо ідентифікувати пісню", color=nextcord.Color.blurple())
                await interaction.send(embed=embed_badlink, ephemeral=True)
                return
        cursor.execute("""INSERT INTO musicLinks VALUES(?, ?, ?, ?, ?, ?)""", (userId, song_link, *attributes, 0))
        conn.commit()
        embed_added = nextcord.Embed(title=f"Успішно додано пісню {attributes[0]} до списку пісень", color=nextcord.Color.blurple())
        await interaction.send(embed=embed_added, ephemeral=True)

bot.run(BOT_KEY)