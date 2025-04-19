import discord
from discord.ext import commands
from discord.ui import View, Button
from discord import Interaction, Embed, PermissionOverwrite
from config import LOG_CHANNEL_ID, SUPPORT_ROLE_ID, MUTE_ROLE_ID, COMMAND_ROLE_ID

# ✅ Check personnalisé pour le rôle autorisé
def has_required_role():
    async def predicate(ctx):
        return discord.utils.get(ctx.author.roles, id=COMMAND_ROLE_ID) is not None
    return commands.check(predicate)

# 🎟️ View avec le bouton d'ouverture de ticket
class TicketButton(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🎟️ Ouvrir un ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket")
    async def open_ticket(self, interaction: Interaction, button: Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: PermissionOverwrite(read_messages=False),
            interaction.user: PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: PermissionOverwrite(read_messages=True, send_messages=True)
        }

        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower().replace(' ', '-')}")
        if existing:
            await interaction.response.send_message("❗ Vous avez déjà un ticket ouvert.", ephemeral=True)
            return

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites,
            reason="Ouverture de ticket"
        )
        await channel.send(f"{interaction.user.mention} 🎫 Voici votre ticket, un membre du staff vous répondra sous peu.")
        await interaction.response.send_message(f"✅ Votre ticket a été créé: {channel.mention}", ephemeral=True)

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_required_role()
    async def ping(self, ctx):
        await ctx.send("Pong! 🏓")

    @commands.command()
    @has_required_role()
    async def crown(self, ctx):
        await ctx.send("👑 The power is mine!")

    @commands.command()
    @has_required_role()
    async def lock(self, ctx):
        role = discord.utils.get(ctx.guild.roles, id=SUPPORT_ROLE_ID)
        if role:
            await ctx.channel.set_permissions(role, send_messages=False)
            await ctx.send(f"🔒 Channel locked for {role.mention}")
        else:
            await ctx.send("Role not found.")

    @commands.command()
    @has_required_role()
    async def unlock(self, ctx):
        role = discord.utils.get(ctx.guild.roles, id=SUPPORT_ROLE_ID)
        if role:
            await ctx.channel.set_permissions(role, send_messages=True)
            await ctx.send(f"🔓 Channel unlocked for {role.mention}")
        else:
            await ctx.send("Role not found.")

    @commands.command()
    @has_required_role()
    async def transcript(self, ctx):
        messages = []
        async for message in ctx.channel.history(limit=100):
            messages.append(f"[{message.created_at}] {message.author}: {message.content}")
        messages.reverse()

        filename = f"transcript-{ctx.channel.name}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(messages))

        await ctx.send(file=discord.File(filename))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlog(self, ctx, channel: discord.TextChannel):
        global LOG_CHANNEL_ID
        LOG_CHANNEL_ID = channel.id
        await ctx.send(f"📒 Log channel set to {channel.mention}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await member.add_roles(role)
            await ctx.send(f"✅ Role {role.name} added to {member.mention}.")
        else:
            await ctx.send("Role not found.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await member.remove_roles(role)
            await ctx.send(f"❌ Role {role.name} removed from {member.mention}.")
        else:
            await ctx.send("Role not found.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def createsalon(self, ctx, *, name):
        await ctx.guild.create_text_channel(name)
        await ctx.send(f"✅ Channel #{name} created.")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def deletesalon(self, ctx, *, name):
        channel = discord.utils.get(ctx.guild.text_channels, name=name)
        if channel:
            await channel.delete()
            await ctx.send(f"🗑️ Channel #{name} deleted.")
        else:
            await ctx.send("Channel not found.")

    @commands.command()
    @has_required_role()
    async def renamesalon(self, ctx, *, new_name: str):
        if ctx.message.channel.type == discord.ChannelType.text:
            await ctx.channel.edit(name=new_name)
            await ctx.send(f"✅ Le salon a été renommé en : {new_name}")
        else:
            await ctx.send("❌ Cette commande ne peut être utilisée que dans un salon textuel.")

    @commands.command()
    @has_required_role()
    async def help(self, ctx):
        embed = discord.Embed(
            title="📖 Available Commands",
            description="Here is the list of commands you can use:",
            color=0xbb00ff
        )
        embed.add_field(name="!ping", value="Replies with Pong!", inline=False)
        embed.add_field(name="!crown", value="Show your royal power 👑", inline=False)
        embed.add_field(name="!lock", value="Locks the channel for a specific role", inline=False)
        embed.add_field(name="!unlock", value="Unlocks the channel for a specific role", inline=False)
        embed.add_field(name="!transcript", value="Records the channel's history", inline=False)
        embed.add_field(name="!setlog #channel", value="Sets the log channel", inline=False)
        embed.add_field(name="!addrole @member Role", value="Adds a role to a member", inline=False)
        embed.add_field(name="!removerole @member Role", value="Removes a role from a member", inline=False)
        embed.add_field(name="!createsalon name", value="Creates a text channel", inline=False)
        embed.add_field(name="!deletesalon name", value="Deletes a text channel", inline=False)
        embed.add_field(name="!renamesalon name", value="Renames the current text channel", inline=False)
        embed.add_field(name="!mute @member", value="Mutes a member with the Muted role", inline=False)
        embed.add_field(name="!unmute @member", value="Unmutes a member (removes Muted role)", inline=False)
        embed.add_field(name="!ticket", value="Creates a private support channel", inline=False)
        embed.add_field(name="!stat", value="Displays server statistics", inline=False)
        embed.add_field(name="!createrole Name permission1 permission2 ...", value="Creates a role with custom permissions", inline=False)
        embed.add_field(name="!payements", value="Displays the classic PayPal link", inline=False)
        embed.add_field(name="!payementsinter", value="Displays the international PayPal link", inline=False)
        embed.add_field(name="!help", value="Displays this help message", inline=False)
        embed.set_footer(text="Crown Bot • Royal Assistance 🤴")
        await ctx.send(embed=embed)

    @commands.command()
    @has_required_role()
    async def stat(self, ctx):
        guild = ctx.guild
        total_members = guild.member_count
        boosts = guild.premium_subscription_count
        boosters = sum(1 for member in guild.members if member.premium_since)

        embed = discord.Embed(
            title=f"📊 Server Statistics: {guild.name}",
            color=0xbb00ff
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👥 Members", value=f"{total_members}", inline=True)
        embed.add_field(name="🚀 Boosts", value=f"{boosts}", inline=True)
        embed.add_field(name="🌟 Boosters", value=f"{boosters}", inline=True)
        embed.set_footer(text=f"Server ID: {guild.id}")

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)
        await member.add_roles(muted_role)
        await ctx.send(f"🔇 {member.mention} has been muted.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"🔊 {member.mention} can now speak.")
        else:
            await ctx.send(f"{member.mention} is not muted.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def createrole(self, ctx, name: str, *, perms: str = ""):
        permissions = discord.Permissions.none()
        perm_names = perms.lower().split()
        valid_perms = [perm for perm in dir(discord.Permissions) if not perm.startswith("_")]

        for perm in perm_names:
            if perm in valid_perms:
                setattr(permissions, perm, True)
            else:
                await ctx.send(f"❌ Unknown permission: {perm}")
                return

        role = await ctx.guild.create_role(name=name, permissions=permissions)
        await ctx.send(f"✅ Role {role.name} created successfully.")

    @commands.command()
    @has_required_role()
    async def payements(self, ctx):
        embed_fr = discord.Embed(
            title="💸 Paiement Classique",
            description="Voici notre lien officiel PayPal pour effectuer un paiement :",
            color=0xbb00ff
        )
        embed_fr.add_field(
            name="🔗 Lien PayPal",
            value="[Cliquez ici pour payer via PayPal](https://www.paypal.me/NexysShop)",
            inline=False
        )
        embed_fr.set_footer(text="Merci pour votre soutien ! ❤️")

        embed_en = discord.Embed(
            title="💸 Classic Payment",
            description="Here is our official PayPal link to make a payment:",
            color=0xbb00ff
        )
        embed_en.add_field(
            name="🔗 PayPal Link",
            value="[Click here to pay via PayPal](https://www.paypal.me/NexysShop)",
            inline=False
        )
        embed_en.set_footer(text="Thank you for your support! ❤️")

        await ctx.send(embed=embed_fr)
        await ctx.send(embed=embed_en)

    @commands.command()
    @has_required_role()
    async def payementsinter(self, ctx):
        embed_fr = discord.Embed(
            title="🌍 Paiement International",
            description="Vous êtes en dehors de notre région principale ? Voici votre lien ! Cliquez ci-dessous pour payer via PayPal.",
            color=0xbb00ff
        )
        embed_fr.add_field(
            name="🔗 Lien PayPal International",
            value="[Cliquez ici pour payer via PayPal](https://paypal.me/NShop710?country.x=BE&locale.x=fr_FR)",
            inline=False
        )
        embed_fr.set_footer(text="Merci pour votre soutien, peu importe où vous êtes ! 💙")

        embed_en = discord.Embed(
            title="🌍 International Payment",
            description="Are you outside our main region? Here is your link! Click below to pay via PayPal.",
            color=0xbb00ff
        )
        embed_en.add_field(
            name="🔗 International PayPal Link",
            value="[Click here to pay via PayPal](https://paypal.me/NShop710?country.x=BE&locale.x=fr_FR)",
            inline=False
        )
        embed_en.set_footer(text="Thank you for your support, no matter where you're from! 💙")

        await ctx.send(embed=embed_fr)
        await ctx.send(embed=embed_en)

# ⚠️ setup to load the cog
async def setup(bot):
    await bot.add_cog(Commands(bot))
    bot.add_view(TicketButton(bot))  # Important pour que les boutons fonctionnent même après restart
