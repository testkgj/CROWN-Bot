import discord
from discord.ext import commands
import asyncio
import os
from config import TOKEN, PREFIX
from keep_alive import keep_alive  # Importation de la fonction keep_alive
import sys

# Ajouter le répertoire courant au chemin de recherche
sys.path.append(os.getcwd())  # Cela ajoute le répertoire actuel au chemin de recherche de Python

# Démarrer le serveur web pour garder le bot en ligne
keep_alive()

# Importer les fichiers commands_lot.py et tickets.py (devra être dans le même dossier que bot.py)
import commands_lot  # Cela va exécuter le contenu de commands_lot.py
import tickets       # Cela va exécuter le contenu de tickets.py

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# ⚠️ Désactivation de la commande help par défaut
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"✅ Bot is ready as {bot.user} ({bot.user.id})")

async def load_cogs():
    """Charge les cogs si nécessaire"""
    for filename in os.listdir("./COGS"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"COGS.{filename[:-3]}")
                print(f"✅ Cog chargé : {filename}")
            except Exception as e:
                print(f"❌ Erreur lors du chargement de {filename} : {e}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())


