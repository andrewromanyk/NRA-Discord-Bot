import nextcord

class replaceSong(nextcord.ui.View):

    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label="Змінити", style = nextcord.ButtonStyle.blurple)
    async def change(self, button: nextcord.ui.Button, interaction: nextcord.Integration):
        #await interaction.send("Ok, changing the song", ephemeral=True)
        self.value = True
        self.stop()

    @nextcord.ui.button(label="Залишити", style = nextcord.ButtonStyle.gray)
    async def leave(self, button: nextcord.ui.Button, interaction: nextcord.Integration):
        #await interaction.send("Ok, the song will reamian the same", ephemeral=True)
        self.value = False
        self.stop()