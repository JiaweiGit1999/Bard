import discord
from discord import app_commands
import discord.context_managers
from player import Player
from discord.ext import tasks
import os
from dotenv import load_dotenv

load_dotenv()

MY_GUILD = ""
guilds = []

with open("cookies.txt", "w", encoding="utf-8") as f:
    f.write(os.getenv("COOKIES_TEXT"))

class MyClient(discord.Client):
    index = 0
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print(f"Connected guilds: {self.guilds}")
        for guild in self.guilds:
            print(f"on_ready: {type(guild)}")
            await self.tree.sync(guild=guild)

    async def on_guild_join(self,guild):
        print(guild.id)
        for guild in self.guilds:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"setup_hook: {type(guild)}")
        await self.tree.sync()
    
    @tasks.loop(seconds=5.0)
    async def player(self):
        vc = None
        if(len(client.voice_clients) > 0):
            vc = client.voice_clients[0]

    async def setup_hook(self):
        self.player.start()
        for guild in self.guilds:
            print(f"setup_hook: {type(guild)}")
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

intents=discord.Intents.all()
client = MyClient(intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")

commandChannelID = None
player = Player(client)

@client.tree.command()
async def stop(interaction: discord.Interaction):
    """Stops the player"""
    await interaction.response.send_message(f'Player Stopped')
    
    vc = client.voice_clients[0]
    vc.stop()
    player.Stop()

@client.tree.command()
async def pause(interaction: discord.Interaction):
    """Pauses the player"""
    await interaction.response.send_message(f'Player Stopped')
    
    vc = client.voice_clients[0]
    vc.pause()

@client.tree.command()
async def resume(interaction: discord.Interaction):
    """Resumes the player"""
    await interaction.response.send_message(f'Player Stopped')
    
    vc = client.voice_clients[0]
    vc.resume()


@client.tree.command()
@app_commands.describe(
    url='url of the song'
)
async def play(interaction: discord.Interaction,  url: str):
    """plays a song."""
    print(f"channel: {interaction.channel.name}")
    if(interaction.channel.name == "song"):
        if(interaction.user.voice != None):
            await interaction.response.send_message(f'Added to Queue: {url}')
            try:
                channel = interaction.user.voice.channel
                vc = await channel.connect()
            except Exception as e:
                server = interaction.guild
                vc = server.voice_client
                print(f"{e}")
            player.Queue(url)
            commandChannelID = interaction.channel_id
            print(f"VC status {player.songQueue}")
            if(vc.is_playing() != True):
                await client.loop.run_in_executor(None,player.Play,player.songQueue.pop(),commandChannelID,False)
        else:
            await interaction.response.send_message(f'Enter a voice channel first')
    else:
        await interaction.response.send_message(f'Wrong Channel')

client.run(TOKEN)