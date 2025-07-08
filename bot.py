import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
FFMPEG_PATH = os.getenv("FFMPEG_PATH")

# Carrega rádios do JSON
RADIO_JSON_PATH = os.path.join(os.path.dirname(__file__), "radios.json")
with open(RADIO_JSON_PATH, "r", encoding="utf-8") as f:
    RADIOS = json.load(f)

# Configuração do bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Quando o bot estiver online
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user.name}")

# Comando para listar rádios disponíveis
@bot.command()
async def radios(ctx):
    lista = '\n'.join(f"• `{nome}`" for nome in RADIOS.keys())
    await ctx.send(f"📻 Rádios disponíveis:\n{lista}")

# Comando para tocar uma rádio
@bot.command()
async def play(ctx, station: str):
    if ctx.author.voice is None:
        await ctx.send("❌ Você precisa estar em um canal de voz.")
        return

    voice_channel = ctx.author.voice.channel

    if station.lower() not in RADIOS:
        await ctx.send(f"❌ Rádio '{station}' não encontrada. Use `!radios` para ver as opções.")
        return

    url = RADIOS[station.lower()]

    # Desconecta se já estiver conectado em outro canal
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

    vc = await voice_channel.connect()

    ffmpeg_options = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": "-vn"
    }

    source = discord.FFmpegPCMAudio(url, executable=FFMPEG_PATH, **ffmpeg_options)
    vc.play(source)

    await ctx.send(f"🎶 Tocando **{station}** agora!")

# Comando para sair do canal de voz
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Saí do canal de voz.")
    else:
        await ctx.send("❌ Não estou em um canal de voz.")

# Inicia o bot
bot.run(TOKEN)
