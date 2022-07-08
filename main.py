import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import random


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix='§')


@bot.event
async def on_ready():
    print(f"{bot.user.name} has sucessfully connected")
    if not os.path.exists('audio'):
        os.mkdir('audio')
    for guild in bot.guilds:
        print(guild.id)
        if not os.path.exists('audio/' + str(guild.id)):
            os.mkdir('audio/' + str(guild.id))
            open(f'audio/{str(guild.id)}/{guild.name}.info', "a").close()


connected_to_voice = False
stopped = False


@bot.command(name='music', aliases=['musik'])
async def music(ctx, repeat: bool = False, i: int = None):
    global connected_to_voice
    global stopped
    directory = os.listdir('audio/' + str(ctx.guild.id))
    audio = [file for file in directory if not file.endswith('.info')]
    if not connected_to_voice:
        vc = await ctx.author.voice.channel.connect()
        connected_to_voice = True
        if i is not None and abs(i) < len(audio):
            file = audio[i]
        else:
            file = random.choice(audio)
        try:
            while not stopped:
                vc.play(discord.FFmpegPCMAudio(f'audio/{str(ctx.guild.id)}/' + file))
                while vc.is_playing() and not stopped:
                    await asyncio.sleep(1)
                vc.stop()
                if not stopped and not repeat:
                    file = random.choice(audio)
        except TypeError:
            pass
        finally:
            await vc.disconnect()
            connected_to_voice = False
            stopped = False


@bot.command(name='stop')
async def stop(ctx, *args):
    global stopped
    if connected_to_voice:
        stopped = True

bot.run(DISCORD_TOKEN)
