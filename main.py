import nextcord
from nextcord.ext import commands
import datetime
import random
import re
import sqlite3
from key import KEY
import python_url


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

    print("Does 0st think work pls")

    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()

    print("Does 1st think work pls")

    try:
        cursor.execute("""CREATE TABLE musicLinks (
                id TEXT,
                link TEXT,
                votes INTEGER
        )""")
    except: 
        print("already exists lmao")

    cursor.execute("""SELECT id FROM musicLinks""")

    musicIds = cursor.fetchall()
    userId = interaction.user.id

    if str(userId) in musicIds: pass
    else:
        cursor.execute("""INSERT INTO musicLinks VALUES (?, ?) """, (userId, song_link))

    print("Done something")
    
    python_url.getSongAttr(song_link)

    conn.commit()

bot.run(BOT_KEY)