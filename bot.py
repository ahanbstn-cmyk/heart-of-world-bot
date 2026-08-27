import os
import sys
import re
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

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT", 10000))

# Safe default intents
intents = discord.Intents.default()
intents.message_content = True

# ----------------- Profanity Filter Wordlist -----------------
PROFANITY_PATTERNS = [
    r'\bfuck\b', r'\bshit\b', r'\bbitch\b', r'\basshole\b', r'\bcunt\b', r'\bdick\b',
    r'\bnigger\b', r'\bnigga\b', r'\bfaggot\b', r'\bwhore\b', r'\bslut\b', r'\bbastard\b',
    r'\bamk\b', r'\baq\b', r'\bsik\b', r'\borospu\b', r'\bpiç\b', r'\byarak\b', r'\bgöt\b'
]
PROFANITY_REGEX = re.compile('|'.join(PROFANITY_PATTERNS), re.IGNORECASE)

class HeartOfWorldBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(VerificationView())
        self.add_view(RoleSelectionView())

    async def on_ready(self):
        print("=" * 60)
        print(f"[ONLINE] Heart Of World Bot is ACTIVE as {self.user} (ID: {self.user.id})")
        print(f"[SERVERS] Connected Guilds ({len(self.guilds)}): {[g.name for g in self.guilds]}")
        print("=" * 60)
        
        # Instantly sync slash commands to each joined guild
        for guild in self.guilds:
            try:
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                print(f"[SYNC] Synced slash commands to {guild.name}")
            except Exception as e:
                print(f"[SYNC ERR] {guild.name}: {e}")

        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name="THE WORLD HIDES SECRETS. • www.nukecell.com"
        )
        await self.change_presence(status=discord.Status.online, activity=activity)

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Check for profanity
        if PROFANITY_REGEX.search(message.content):
            try:
                await message.delete()
                warning = await message.channel.send(
                    f"⚠️ {message.author.mention}, profanity and offensive language are strictly prohibited in the Heart Of World archives."
                )
                await asyncio.sleep(5)
                await warning.delete()
                print(f"[AUTO-MOD] Deleted offensive message from {message.author.name}")
            except Exception as e:
                print(f"[AUTO-MOD ERR] {e}")
            return

        await self.process_commands(message)

bot = HeartOfWorldBot()

# ----------------- Interactive Views (Buttons) -----------------

class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Accept Rules & Clear Access", style=discord.ButtonStyle.success, emoji="✅", custom_id="verify_button_persistent")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name="Investigator") or discord.utils.get(guild.roles, name="Explorer")
        if not role:
            try:
                role = await guild.create_role(name="Investigator", color=discord.Color.teal(), reason="Auto-created for verification")
            except Exception:
                await interaction.response.send_message("⚠️ Error creating role. Please grant 'Manage Roles' permission to the bot!", ephemeral=True)
                return

        if role in interaction.user.roles:
            await interaction.response.send_message("ℹ️ You already have clearance and hold the **Investigator** role!", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(f"🎉 **Clearance Granted!** You have been assigned the **{role.name}** role.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("⚠️ Please place the Bot role above other roles in Server Settings!", ephemeral=True)


class RoleSelectionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Launch Ping Squad", style=discord.ButtonStyle.primary, emoji="🔔", custom_id="role_launch_ping")
    async def launch_ping(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, "Launch Squad", "You will be alerted the second Kickstarter goes LIVE! 🚀")

    @discord.ui.button(label="North America (NA)", style=discord.ButtonStyle.secondary, emoji="🌎", custom_id="role_region_na")
    async def region_na(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, "Region: NA", "North America regional clearance updated!")

    @discord.ui.button(label="Europe (EU)", style=discord.ButtonStyle.secondary, emoji="🌍", custom_id="role_region_eu")
    async def region_eu(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, "Region: EU", "Europe regional clearance updated!")

    async def _toggle_role(self, interaction: discord.Interaction, role_name: str, message: str):
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            try:
                role = await guild.create_role(name=role_name, reason="Auto-created for role selector")
            except Exception:
                await interaction.response.send_message(f"⚠️ Could not create `{role_name}` role.", ephemeral=True)
                return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ Removed **{role_name}** role.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Added **{role_name}** role! {message}", ephemeral=True)


# ----------------- Server Setup Core Logic -----------------

async def execute_server_setup(guild: discord.Guild, status_channel=None):
    # 1. Category: ARCHIVES & RULES
    cat_info = discord.utils.get(guild.categories, name="📌 ARCHIVES & RULES") or await guild.create_category("📌 ARCHIVES & RULES")

    # 2. Category: CLASSIFIED DOSSIERS
    cat_cards = discord.utils.get(guild.categories, name="🗂️ CLASSIFIED DOSSIERS") or await guild.create_category("🗂️ CLASSIFIED DOSSIERS")

    # 3. Category: INVESTIGATOR HUBS (Text Chat)
    cat_chat = discord.utils.get(guild.categories, name="🌍 INVESTIGATOR HUBS") or await guild.create_category("🌍 INVESTIGATOR HUBS")

    # Create Channels in ARCHIVES & RULES
    c_rules = discord.utils.get(guild.text_channels, name="welcome-rules")
    if not c_rules:
        c_rules = await guild.create_text_channel("welcome-rules", category=cat_info)
        embed_v = discord.Embed(
            title="🛡️ Welcome to Heart Of World — Security Protocol",
            description=(
                "**THE WORLD HIDES SECRETS.**\n\n"
                "Welcome to the official investigation hub of Heart Of World (Designed by NukeCell).\n\n"
                "**Investigation Rules:**\n"
                "• Respect all fellow investigators. Zero tolerance for toxicity.\n"
                "• Profanity and offensive language are strictly prohibited and auto-filtered.\n"
                "• Keep discussions in the relevant regional channels.\n"
                "• Follow official updates on the 600 First Edition Cards & Kickstarter.\n\n"
                "🌐 **Official Portal:** [www.nukecell.com](https://www.nukecell.com)\n\n"
                "Click the button below to obtain clearance:"
            ),
            color=discord.Color.green()
        )
        await c_rules.send(embed=embed_v, view=VerificationView())

    c_about = discord.utils.get(guild.text_channels, name="about-heart-of-world")
    if not c_about:
        c_about = await guild.create_text_channel("about-heart-of-world", category=cat_info)
        embed_a = discord.Embed(
            title="🃏 HEART OF WORLD — THE WORLD HIDES SECRETS",
            description=(
                "**Developer & Design:** NukeCell ([www.nukecell.com](https://www.nukecell.com))\n"
                "**Genre:** CCS – Collectible Card Story\n"
                "**Core Focus:** Mystery, Lore, Real Documented Phenomena & High-Value Collecting\n\n"
                "Heart Of World is an original universe inspired by real documented events throughout human history, unsolved mysteries, and classified occurrences.\n\n"
                "Here, cards are not just for collecting.\n"
                "**Every card is a piece of a classified case file.**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "### 🗂️ THE THREE PILLARS\n\n"
                "👻 **PARANORMAL**\n"
                "Documented paranormal cases, classified witness testimonies, scientific investigations, and mysteries that still defy explanation.\n\n"
                "📻 **FREQUENCY**\n"
                "Iconic leaders, historical figures, notorious minds, and mythological archetypes that resonated across time.\n\n"
                "💥 **ANOMALY**\n"
                "Cataclysms, historical disasters, reality rifts, and world-altering phenomena that reshaped the human timeline.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "### ⬛ BLACK FILES & CONTINUITY\n"
                "• 🔗 **Case Continuity:** Single incidents span multiple sequential cards. Assemble the chain to decode the full dossier.\n"
                "• 🗂️ **Public Files:** Declassified records accessible to all.\n"
                "• 📁 **Classified Dossiers:** Restricted files requiring deeper investigation.\n"
                "• ⬛ **BLACK FILE:** Ultra-rare, serialized pieces revealed through special events.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "### 🌌 A MASSIVE LIVING UNIVERSE\n"
                "• 🏛️ **25 Main Seasons • 75 Sub-Seasons**\n"
                "• 🎴 **600 Limited First Edition Serialized Prints**\n"
                "• 👑 **Ultra-Rare 1-of-1 Anomaly Cards & Black File Relics**\n\n"
                "🌐 **Official Portal:** [www.nukecell.com](https://www.nukecell.com)\n"
                "🚀 **Kickstarter Launching VERY SOON!**"
            ),
            color=0x111111
        )
        await c_about.send(embed=embed_a)

    c_roles = discord.utils.get(guild.text_channels, name="roles-and-notifications")
    if not c_roles:
        c_roles = await guild.create_text_channel("roles-and-notifications", category=cat_info)
        embed_r = discord.Embed(
            title="🎭 Select Notification & Region Roles",
            description="Equip your clearance roles below:",
            color=discord.Color.blurple()
        )
        await c_roles.send(embed=embed_r, view=RoleSelectionView())

    c_kick = discord.utils.get(guild.text_channels, name="kickstarter-updates")
    if not c_kick:
        c_kick = await guild.create_text_channel("kickstarter-updates", category=cat_info)
        embed_k = discord.Embed(
            title="🚀 Heart Of World — Official Kickstarter Hub",
            description=(
                "Our Kickstarter campaign is launching **VERY SOON**!\n\n"
                "• 🎴 **600 Serialized First Edition Box Sets** (Physical Prints)\n"
                "• ⬛ **Exclusive Stamped Black File Cards** (Never Reprinted)\n"
                "• 📱 **Mobile In-Game Secret Dossiers & Founder Badges**\n"
                "• 🌐 **Official Website:** [www.nukecell.com](https://www.nukecell.com)\n"
                "• 💰 **Day-1 Early Bird Special Discounts**"
            ),
            color=discord.Color.gold()
        )
        embed_k.add_field(name="🔗 Kickstarter Pre-Launch", value="[👉 Click Here to Follow & Get Notified](https://kickstarter.com)", inline=False)
        await c_kick.send(embed=embed_k)

    # Create Channels in CLASSIFIED DOSSIERS
    if not discord.utils.get(guild.text_channels, name="case-file-announcements"):
        await guild.create_text_channel("case-file-announcements", category=cat_cards)
    if not discord.utils.get(guild.text_channels, name="black-file-theories"):
        await guild.create_text_channel("black-file-theories", category=cat_cards)

    # Create Channels in INVESTIGATOR HUBS
    regional_channels = [
        "general-investigation",
        "theories-and-clues",
        "north-america",
        "europe-general",
        "france-francais",
        "italy-italiano",
        "germany-deutsch",
        "spain-espanol",
        "feedback-and-ideas"
    ]
    for ch_name in regional_channels:
        if not discord.utils.get(guild.text_channels, name=ch_name):
            await guild.create_text_channel(ch_name, category=cat_chat)

    if status_channel:
        await status_channel.send("✅ **Heart Of World Investigation Hub is LIVE!** All text archives, rules, regional hubs, and auto-moderation have been configured.")


# ----------------- Commands (Both Slash & Prefix !setup) -----------------

@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup_prefix(ctx):
    await ctx.send("⚙️ Setting up Heart Of World server archives...")
    await execute_server_setup(ctx.guild, ctx.channel)

@bot.tree.command(name="setup_full_server", description="[Admin] Set up all classified categories, dossiers & regional text channels")
@app_commands.checks.has_permissions(administrator=True)
async def setup_slash(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await execute_server_setup(interaction.guild)
    await interaction.followup.send("✅ **Heart Of World Investigation Hub is LIVE!**", ephemeral=True)


@bot.tree.command(name="about", description="Learn about the Heart Of World Collectible Card Story universe")
async def about(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🃏 HEART OF WORLD — THE WORLD HIDES SECRETS",
        description=(
            "**Design & Development:** NukeCell ([www.nukecell.com](https://www.nukecell.com))\n"
            "**Genre:** CCS – Collectible Card Story\n\n"
            "Heart Of World is an original universe inspired by real documented events throughout human history, unsolved mysteries, and classified occurrences.\n\n"
            "📂 **3 Main Pillars:**\n"
            "• 👻 **PARANORMAL:** Unexplained phenomena & documented historical anomalies.\n"
            "• 📻 **FREQUENCY:** Iconic historical leaders, key figures & mythos.\n"
            "• 💥 **ANOMALY:** Catastrophes, civilization-altering events & reality rifts.\n\n"
            "🗂️ **Story Continuity & Black Files:**\n"
            "Cards form interconnected case files. Certain stories span multiple continuation cards that collectors assemble to decode the full dossier.\n\n"
            "🌌 **Scope:** 25 Main Seasons • 75 Sub-Seasons • 600 First Edition Cards.\n"
            "🌐 **Official Portal:** [www.nukecell.com](https://www.nukecell.com)"
        ),
        color=0x111111
    )
    embed.set_footer(text="Use /socials to follow NukeCell & official updates!")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="kickstarter", description="Kickstarter status and First Edition collector box info")
async def kickstarter(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🚀 Heart Of World — Kickstarter Launching VERY SOON!",
        description=(
            "🔥 **The 600-Card Premier Investigation Begins!**\n\n"
            "By backing on Kickstarter, collectors secure:\n"
            "• 🗂️ **First Edition Serialized Box Sets** (Physical Stamped Foil Prints)\n"
            "• ⬛ **Exclusive Black File Foil Cards** (Never Reprinted)\n"
            "• 📱 **Mobile In-Game Secret Dossiers & Founder Badges**\n"
            "• 🌐 **Official Portal:** [www.nukecell.com](https://www.nukecell.com)\n"
            "• 👑 **Lifetime Backer Clearance Role in Discord**\n"
            "• 💰 **Day-1 Early Bird Special Tier Discounts**"
        ),
        color=discord.Color.gold()
    )
    embed.add_field(name="🔗 Kickstarter Pre-Launch Page", value="[👉 Click Here to Follow & Get Notified](https://kickstarter.com)", inline=False)
    embed.add_field(name="⏳ Status", value="**LAUNCHING VERY SOON**", inline=True)
    embed.add_field(name="🎴 Series", value="**600 First Edition Prints (NukeCell CCS)**", inline=True)
    embed.set_footer(text="Heart Of World • The World Hides Secrets • www.nukecell.com", icon_url=bot.user.display_avatar.url if bot.user else None)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="socials", description="Official links and archives")
async def socials(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔗 Official Channels & Archives",
        description="Follow Heart Of World across all official platforms:",
        color=discord.Color.blue()
    )
    embed.add_field(name="🌐 Official Website", value="[www.nukecell.com](https://www.nukecell.com)", inline=False)
    embed.add_field(name="🚀 Kickstarter", value="[Pre-Launch Page](https://kickstarter.com)", inline=False)
    embed.add_field(name="🐦 Twitter / X", value="[Follow @HeartOfWorld](https://twitter.com)", inline=True)
    embed.add_field(name="📺 YouTube", value="[Watch Case Files & Teasers](https://youtube.com)", inline=True)
    embed.set_footer(text="NukeCell CCS • www.nukecell.com")
    await interaction.response.send_message(embed=embed)


# ----------------- Health Check Server for Render -----------------

async def handle_ping(request):
    return web.Response(text="Heart Of World (NukeCell CCS) Bot is Online • www.nukecell.com 🚀")

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
        print("[ERR] DISCORD_TOKEN is missing!")
        return
    await start_web_server()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
