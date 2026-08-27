import os
import sys
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from aiohttp import web

# Ensure UTF-8 output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT", 10000))

# Setup Intents
intents = discord.Intents.default()

class HeartOfWorldBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Register persistent interactive views
        self.add_view(VerificationView())
        self.add_view(RoleSelectionView())
        
        # Sync slash commands globally
        print("[*] Syncing slash commands to Discord...")
        try:
            synced = await self.tree.sync()
            print(f"[OK] Synced {len(synced)} slash command(s) successfully.")
        except Exception as e:
            print(f"[WARN] Error syncing slash commands: {e}")

    async def on_ready(self):
        print("=" * 60)
        print(f"[ONLINE] Heart Of World Bot is ACTIVE as {self.user} (ID: {self.user.id})")
        print(f"[SERVERS] Connected Guilds ({len(self.guilds)}): {[g.name for g in self.guilds]}")
        print("=" * 60)
        
        # Set rich presence activity
        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name="Heart Of World on Kickstarter 🚀"
        )
        await self.change_presence(status=discord.Status.online, activity=activity)

bot = HeartOfWorldBot()

# ----------------- Interactive Views (Buttons) -----------------

class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Accept Rules & Verify", 
        style=discord.ButtonStyle.success, 
        emoji="✅", 
        custom_id="verify_button_persistent"
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name="Explorer") or discord.utils.get(guild.roles, name="Member")
        
        if not role:
            try:
                role = await guild.create_role(name="Explorer", color=discord.Color.blue(), reason="Auto-created by bot for verification")
            except Exception as e:
                await interaction.response.send_message("⚠️ Could not create role. Please ensure bot has 'Manage Roles' permission!", ephemeral=True)
                return

        if role in interaction.user.roles:
            await interaction.response.send_message("ℹ️ You are already verified and have the **Explorer** role!", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"🎉 **Welcome to Heart Of World!** You have been verified and given the **{role.name}** role.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("⚠️ Bot does not have permission to assign roles. Move the Bot's role above other roles in Server Settings!", ephemeral=True)


class RoleSelectionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Launch Ping Squad", 
        style=discord.ButtonStyle.primary, 
        emoji="🔔", 
        custom_id="role_launch_ping"
    )
    async def launch_ping(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, "Launch Squad", "You will be pinged when our Kickstarter campaign goes LIVE! 🚀")

    @discord.ui.button(
        label="North America (NA)", 
        style=discord.ButtonStyle.secondary, 
        emoji="🌎", 
        custom_id="role_region_na"
    )
    async def region_na(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, "Region: NA", "North America region role updated!")

    @discord.ui.button(
        label="Europe (EU)", 
        style=discord.ButtonStyle.secondary, 
        emoji="🌍", 
        custom_id="role_region_eu"
    )
    async def region_eu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, "Region: EU", "Europe region role updated!")

    async def _toggle_role(self, interaction: discord.Interaction, role_name: str, message: str):
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            try:
                role = await guild.create_role(name=role_name, reason="Auto-created for role selector")
            except Exception:
                await interaction.response.send_message(f"⚠️ Could not create/find `{role_name}` role. Please check bot permissions.", ephemeral=True)
                return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Removed **{role_name}** role.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Added **{role_name}** role! {message}", ephemeral=True)


# ----------------- Slash Commands -----------------

@bot.tree.command(name="kickstarter", description="Get official Kickstarter campaign details and links")
async def kickstarter(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🚀 Heart Of World — Official Kickstarter Campaign",
        description=(
            "Welcome to the official Kickstarter hub for **Heart Of World**!\n\n"
            "Support our journey to bring this unique universe to life. Early backers receive exclusive in-game rewards, physical collector items, and early alpha access."
        ),
        color=discord.Color.gold()
    )
    embed.add_field(name="🔗 Campaign Page", value="[👉 Click Here to Visit Kickstarter](https://kickstarter.com)", inline=False)
    embed.add_field(name="🎯 Status", value="**Pre-Launch (Coming Soon)**", inline=True)
    embed.add_field(name="🎁 Early Bird Perks", value="Special Discord Role & Discounted Tiers", inline=True)
    embed.set_footer(text="Heart Of World • Thank you for your support!", icon_url=bot.user.display_avatar.url if bot.user else None)
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="about", description="Learn more about the Heart Of World project")
async def about(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌍 About Heart Of World",
        description=(
            "**Heart Of World** is an ambitious world-building project and adventure game developed for players across Europe, North America, and worldwide.\n\n"
            "✨ **Key Highlights:**\n"
            "• Rich immersive lore & diverse fantasy realms\n"
            "• Community-driven story and alpha playtests\n"
            "• Cross-platform experience & regular devlogs"
        ),
        color=discord.Color.purple()
    )
    embed.add_field(name="🎮 Platforms", value="PC / Steam (Stretch goals for Consoles)", inline=True)
    embed.add_field(name="🌐 Community", value="Global (English Primary)", inline=True)
    embed.set_footer(text="Use /socials to connect with us everywhere!")
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="socials", description="Official social media and website links")
async def socials(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔗 Official Links & Social Media",
        description="Stay connected with our latest updates across all official channels:",
        color=discord.Color.blue()
    )
    embed.add_field(name="🚀 Kickstarter", value="[Kickstarter Pre-Launch](https://kickstarter.com)", inline=False)
    embed.add_field(name="🐦 Twitter / X", value="[Follow on X](https://twitter.com)", inline=True)
    embed.add_field(name="📺 YouTube", value="[Watch Devlogs & Trailers](https://youtube.com)", inline=True)
    embed.add_field(name="🌐 Website", value="[Official Website](https://google.com)", inline=True)
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="faq", description="Frequently Asked Questions about Kickstarter & the project")
async def faq(interaction: discord.Interaction):
    embed = discord.Embed(
        title="❓ Frequently Asked Questions (FAQ)",
        color=discord.Color.teal()
    )
    embed.add_field(
        name="Q: When does the Kickstarter launch?",
        value="A: We are currently in the pre-launch phase! Click the notification button in `#roles` or use `/kickstarter` to get notified the second we go live.",
        inline=False
    )
    embed.add_field(
        name="Q: How do I get the Backer Discord role?",
        value="A: Once you pledge on Kickstarter, our team / verification system will grant you the exclusive Backer role and access to `#backer-exclusive-chat`.",
        inline=False
    )
    embed.add_field(
        name="Q: What languages will be supported?",
        value="A: English is our primary language. Subtitles and localizations will be introduced as stretch goals during the campaign.",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)


# ----------------- Admin Setup Commands -----------------

@bot.tree.command(name="post_verify_panel", description="[Admin] Post the verification button panel in this channel")
@app_commands.checks.has_permissions(administrator=True)
async def post_verify_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛡️ Welcome to Heart Of World — Verification",
        description=(
            "Welcome to the official **Heart Of World** international community!\n\n"
            "To gain full access to the server and channels, please ensure you respect everyone and follow our community rules.\n\n"
            "Click the button below to verify and unlock the channels:"
        ),
        color=discord.Color.green()
    )
    await interaction.channel.send(embed=embed, view=VerificationView())
    await interaction.response.send_message("✅ Verification panel posted successfully!", ephemeral=True)


@bot.tree.command(name="post_roles_panel", description="[Admin] Post self-assignable roles panel in this channel")
@app_commands.checks.has_permissions(administrator=True)
async def post_roles_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎭 Notification & Region Roles",
        description=(
            "Customize your experience by selecting your roles below:\n\n"
            "🔔 **Launch Ping Squad:** Get notified when Kickstarter launches!\n"
            "🌎 **Region NA:** For North American timezone announcements & events\n"
            "🌍 **Region EU:** For European timezone announcements & events"
        ),
        color=discord.Color.blurple()
    )
    await interaction.channel.send(embed=embed, view=RoleSelectionView())
    await interaction.response.send_message("✅ Roles panel posted successfully!", ephemeral=True)


# ----------------- Health Check Web Server for Render -----------------

async def handle_ping(request):
    return web.Response(text="Heart Of World Discord Bot is Online 🚀")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"[WEB] Health check server listening on port {PORT}")


async def main():
    if not TOKEN:
        print("[ERR] DISCORD_TOKEN is missing in environment variables!")
        return
    # Start web server and bot concurrently
    await start_web_server()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
