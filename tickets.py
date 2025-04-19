import discord
from discord.ext import commands
from discord.ui import View, Button
from config import LOG_CHANNEL_ID, SUPPORT_ROLE_ID

class TicketButtons(View):
    def __init__(self, author):
        super().__init__(timeout=None)
        self.author = author

    @discord.ui.button(label="Fermer le ticket", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"📁 Ticket fermé : {interaction.channel.name} par {interaction.user.mention}")
        await interaction.channel.delete()

    @discord.ui.button(label="Ajouter rôle", style=discord.ButtonStyle.success)
    async def add_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(SUPPORT_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Rôle {role.name} ajouté à {interaction.user.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message("Rôle introuvable (vérifie l'ID dans config.py).", ephemeral=True)

    @discord.ui.button(label="Ping l'utilisateur", style=discord.ButtonStyle.primary)
    async def ping_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"🔔 {self.author.mention}, on s'occupe de toi !",
            allowed_mentions=discord.AllowedMentions(users=True)
        )

class TicketOpener(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Ouvrir un ticket", style=discord.ButtonStyle.success)
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ticket_channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        embed = discord.Embed(
            title="🎫 Ticket Ouvert",
            description="Bienvenue ! Un membre du staff va bientôt vous aider.",
            color=0x00ff00
        )
        await ticket_channel.send(content=f"{interaction.user.mention}", embed=embed, view=TicketButtons(interaction.user))
        await interaction.response.send_message(f"✅ Ton ticket a été ouvert ici : {ticket_channel.mention}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ticket(self, ctx):
        """Commande pour envoyer le bouton d’ouverture de ticket."""
        embed = discord.Embed(
            title="📩 Ouvre un ticket",
            description="Clique sur le bouton ci-dessous pour ouvrir un ticket.",
            color=0xbb00ff
        )
        await ctx.send(embed=embed, view=TicketOpener())

# ⚙️ Setup async requis
async def setup(bot):
    await bot.add_cog(Tickets(bot))
