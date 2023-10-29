import nextcord
import sqlite3

def dbVote(id, songtovote):
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("""UPDATE musicLinks SET votes = votes + 1 WHERE name = ?""", (songtovote, ))
        cursor.execute("""INSERT INTO voted VALUES(?, ?)""", (id, songtovote))
        conn.commit()
        conn.close()

class dropdownVote(nextcord.ui.Select):
    def __init__(self):
        names = [u[0] for u in sqlite3.connect("bot.db").cursor().execute("""SELECT name FROM musicLinks""").fetchall()]
        options = [nextcord.SelectOption(label=u, value=u) for u in names]
        super().__init__(placeholder='Оберіть пісню', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction): 
        dbVote(interaction.user.id, self.values[0])

        embed_voted = nextcord.Embed(title=f"Ви успішно прогосували за {self.values[0]}", color=nextcord.Color.blurple())
        await interaction.send(embed=embed_voted, ephemeral=True)

    
class dropdownView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        dropdown = dropdownVote()
        self.add_item(dropdown)
    
    def values(self):
        return self.children[0].values    
    
