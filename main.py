import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import random
import yt_dlp


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
    directory = os.listdir('audio/' + str(ctx.guild.id) + '/saved')
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
                vc.play(discord.FFmpegPCMAudio(f'audio/{str(ctx.guild.id)}/' + '/saved/' + file))
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


@bot.command(name='play')
async def play(ctx, url: str):
    global connected_to_voice
    global stopped
    print(url)
    if not connected_to_voice:
        song_path = 'audio/' + str(ctx.guild.id) + '/song.mp3'
        song_isfile = os.path.isfile(song_path)
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }
        try:
            if song_isfile:
                os.remove('audio/' + str(ctx.guild.id) + '/song.mp3')
        except PermissionError:
            await ctx.send("stop currently playing(§stop) to play new song")
        vc = await ctx.author.voice.channel.connect()
        connected_to_voice = True
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        for file in os.listdir('./'):
            if file.endswith('.mp3'):
                os.rename(file, 'audio/' + str(ctx.guild.id) + '/song.mp3')
        try:
            vc.play(discord.FFmpegPCMAudio(f'audio/{str(ctx.guild.id)}/' + 'song.mp3'))
            while vc.is_playing() and not stopped:
                await asyncio.sleep(1)
            vc.stop()
        except TypeError:
            pass
        finally:
            await vc.disconnect()
            connected_to_voice = False
            stopped = False


bot.run(DISCORD_TOKEN)
