import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()  # Carrega o .env

TOKEN = os.getenv("DISCORD_TOKEN")
FFMPEG_PATH = os.getenv("FFMPEG_PATH")
RADIO_URL = "https://servidor22-2.brlogic.com:7076/live?source=8542"

print(f"Token carregado: {TOKEN[:5]}...")  # mostra os 5 primeiros caracteres do token


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name}')

@bot.command(name='join')
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()

        ffmpeg_options = {
            'options': '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        }

        source = discord.FFmpegPCMAudio(RADIO_URL, executable=FFMPEG_PATH, **ffmpeg_options)

        def after_playing(error):
            if error:
                print(f"Erro no áudio: {error}")
            else:
                print("Stream finalizado ou interrompido.")

        voice_client.play(source, after=after_playing)
        await ctx.send(f"🎶 Tocando a rádio no canal **{channel.name}**!")
    else:
        await ctx.send("❌ Você precisa estar em um canal de voz.")

@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Saí do canal de voz.")
    else:
        await ctx.send("❌ Eu não estou em um canal de voz.")

bot.run(TOKEN)
