import os
import discord
import json
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from colorama import init, Fore
from typing import Dict, Any

# ---------------- Logging ---------------- # 
# SHOUTOUT EIGHTBY8
def log(message: str, level: str = "INFO") -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    colors = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "INIT": Fore.MAGENTA
    }
    color = colors.get(level, "")
    print(color + f"[{timestamp}] [{level}] {message}")

# Initalize colorama
init(autoreset=True)

load_dotenv()

# ---------------- Globals ---------------- #
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
OWNER_ID = os.getenv("OWNER_ID")
CONFIG_FILE = "config.json"

if not TOKEN:
    log("'DISCORD_TOKEN' is not set in the environment", "ERROR")
else: 
    log("'DISCORD_TOKEN' Loaded", "SUCCESS")

# ---------------- In-Memory States ---------------- #
userReactions: Dict[int, list[str]] = {}



# ---------------- Bot Setup ---------------- #
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ---------------- Save/Load Config ---------------- #
def saveConfig():
    """Save the current CHANNEL_ID to a JSON file."""
    data = {
        "channel_id": CHANNEL_ID,
        "owner_id": OWNER_ID,
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    log(f"Configuration saved to {CONFIG_FILE}", "SUCCESS")

def loadConfig():
    """Load configuration from JSON; create it with defaults if missing."""
    global CHANNEL_ID, OWNER_ID, PING_ROLE_ID
    
    #  Check if file exists. If not, create it with current global values.
    if not os.path.exists(CONFIG_FILE):
        log(f"{CONFIG_FILE} not found. Creating a new one with defaults...", "WARNING")
        saveConfig() 
        return

    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)

            CHANNEL_ID = data.get("channel_id", CHANNEL_ID)
            OWNER_ID = data.get("owner_id", OWNER_ID)
            
            log(f"Configuration loaded from {CONFIG_FILE}", "SUCCESS")
    except Exception as e:
        log(f"Failed to load config: {e}", "ERROR")



# ---------------- Bot Setup ---------------- #
@bot.event
async def on_ready():
    # Sync Commands
    try:
        synced = await bot.tree.sync()
        log(f"Synced {len(synced)} slash commands", "INFO")
    except Exception as e:
        log(f"Failed to sync commands: {e}", "ERROR")

    # Bot Status | Version number
    versionNumber = "v0.0.3"
    await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name=versionNumber)
            )

    global OWNER_ID
    log(f"Logged in as {bot.user} | {versionNumber}", "SUCCESS")

    if OWNER_ID is None:
        if GUILD_ID:
            try:
                guild_id = int(GUILD_ID)
                guild = bot.get_guild(guild_id)
                
                if not guild:
                    guild = await bot.fetch_guild(guild_id)

                if guild:
                    OWNER_ID = guild.owner_id
                    ownerName = guild.get_member(OWNER_ID) or await guild.fetch_member(OWNER_ID)
                    log(f"Auto-configured Owner: {ownerName} ({OWNER_ID})", "INIT")
                    saveConfig()
                else:
                    log(f"Could not find guild with ID {guild_id}", "ERROR")
            except ValueError:
                log("GUILD_ID in .env is not a valid number!", "ERROR")
        else:
            log("GUILD_ID is missing from your .env file!", "ERROR")

# ---------------- Bot Events ---------------- #
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionData) -> None:
    if payload.user_id == bot.user.id:
        return

    if payload.emoji.name == "📌":
        try:
            user = bot.get_user(payload.user_id) or await bot.fetch_user(payload.user_id)
            channel = bot.get_channel(payload.channel_id) or await bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            if message.author.bot:
                return

            if CHANNEL_ID:
                target_id = int(CHANNEL_ID)
                target_channel = bot.get_channel(target_id) or await bot.fetch_channel(target_id)
                reactorName = user.name.capitalize()
                view = CreateEmbed(data=message.content, title=f"📌 New Message Pinned | {reactorName}")
                await target_channel.send(embed=view.pinEmbed())
                log(f"Message Pinned | Channel: [#{channel.name}] | Author of Message: {message.author.name} | Message: {message.content} | Pin User: {reactorName}", "INFO")
            else:
                log("Pin detected, but 'CHANNEL_ID' is not configured.", "WARNING")

        except Exception as e:
            log(f"Failed to process pin: {e}", "ERROR") 

@bot.event
async def on_raw_reaction_remove(content: discord.RawReactionData) -> None:
    if content.emoji.name == "📌":
        try:
            channel = bot.get_channel(content.channel_id) or await bot.fetch_channel(content.message_id)
            message = await channel.fetch_message(content.message_id)
            log(f"Message removed | Channel: [#{channel.name}] | Message: {message.content[:25]}...","INFO")

        except Exception as e:
            log(f"Failed to fetch message for pin: {e}", "ERROR")

# ---------------- Commands ---------------- #
@tree.command(name="setchannel", description="Set the channel where all pins will be sent")
async def set_channel(interaction: discord.Interaction) -> None:
    global CHANNEL_ID
    
    if OWNER_ID is None:
        log("Permission check failed: OWNER_ID is not set in .env or config.", "ERROR")
        return await interaction.response.send_message("Bot configuration error: Owner ID not found.", ephemeral=True)

    if interaction.user.id != int(OWNER_ID):
        return await interaction.response.send_message("You do not have permission to set channels.", ephemeral=True)

    CHANNEL_ID = interaction.channel.id
    saveConfig()

    await interaction.response.send_message(f"Pinboard channel set to: {interaction.channel.mention}")
    log(f"Pinboard channel set to {interaction.channel.id} by {interaction.user.name.capitalize()}", "INFO")

@tree.command(name="testembed", description="Spawn a test embed")
async def testEmbed(interaction: discord.Interaction):
    await interaction.response.defer() 

    try:
        view = CreateEmbed(data="Test Data", title="Test Pin") 
        embed = view.pinEmbed()

        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        log(f"Error in testEmbed: {e}", "ERROR")
        await interaction.followup.send("An error occurred while generating the embed.")


# ---------------- UI / Embeds ---------------- #
class CreateEmbed(discord.ui.View):
    def __init__(self, data, timeout=180, title="", description="", color=0xffffff):
        super().__init__(timeout=timeout)
        self.data = data 
        self.titleText = title
        self.descText = description  
        self.color = color

    def pinEmbed(self):
        embed = discord.Embed(
            title=f"{self.titleText}",
            description = str(self.data),
            color=0xFFFFFF,
        )
        return embed

# ---------------- Run ---------------- #
def main():
    loadConfig()
    log("'CONFIG_FILE' Loaded", "SUCCESS")

    try:
        bot.run(TOKEN)
    except Exception as e:
        log(f"Failed to start bot: {e}", "ERROR")

if __name__ == "__main__":
    main()
