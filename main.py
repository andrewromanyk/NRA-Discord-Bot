import nextcord
from nextcord.ext import commands
import datetime
import random
import re

BOT_KEY = " "

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

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
    )
    ):

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

    print(f"Created role named {role_name} and colored {rgb_list}")



bot.run(BOT_KEY)