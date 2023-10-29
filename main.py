import nextcord
from nextcord.ext import commands
import datetime, time, asyncio, json
import random
import re
import sqlite3, schedule, pytz
from key import KEY
import cogs

BOT_KEY = KEY
RATING_IN_PROCESS = True

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="l.", intents=intents)
@bot.event
async def on_ready():
    print(f"Started working at {datetime.datetime.utcnow()}")


def createDB():
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

    try:
        cursor.execute("""CREATE TABLE voted (
                id TEXT,
                name TEXT
        )""")
    except: pass
    conn.commit()
    conn.close()
    
createDB()

async def forAdmin(interaction: nextcord.Interaction):
    if not interaction.permissions.administrator:
        embed_notadmin = nextcord.Embed(title=f"Ви не можете використати цю команду\nНеобхідні права адміністратора", color=nextcord.Color.blurple())
        await interaction.send(embed=embed_notadmin, ephemeral=True)
        return False
    return True

bot.add_cog(cogs.sovo.SongVote(bot))

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

    if not await forAdmin(interaction): return

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

    embed_createrole = nextcord.Embed(title=f"{interaction.user.name} створив роль '{role.name}' для {user.name}", color=nextcord.Color.blurple())
    await interaction.send(embed=embed_createrole)



bot.run(BOT_KEY)