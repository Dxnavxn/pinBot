import os
import discord
import json
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from colorama import init, Fore

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

# ---------------- Defaults ---------------- #
DEFAULT_CHANNEL_ID: int = None 




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
        saveConfig() # This writes the current globals to a new file
        return

    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)

            CHANNEL_ID = data.get("channel_id", CHANNEL_ID)
            OWNER_ID = data.get("owner_id", OWNER_ID)
            
            log(f"Configuration loaded from {CONFIG_FILE}", "SUCCESS")
    except Exception as e:
        log(f"Failed to load config: {e}", "ERROR")


# ---------------- Commands ---------------- #
@tree.command(name="setchannel", description="Set the channel where all embeds will be sent")
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

@bot.event
async def on_ready():

    # Bot Status | Version number
    versionNumber = "v0.1"
    await bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name=versionNumber)
            )

    global OWNER_ID
    log(f"Logged in as {bot.user} | {versionNumber}", "SUCCESS")

    if OWNER_ID is None:
        if GUILD_ID:
            try:
                # Convert the string from .env to an integer here
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
