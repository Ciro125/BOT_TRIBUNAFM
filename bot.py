import discord
import yt_dlp
from discord.ext import commands
from collections import deque
from functools import partial
import os
import json
import asyncio
from dotenv import load_dotenv

# Fila de musicas
queues = {}  # dicionário com ID do servidor -> fila de músicas

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

# Função para tocar a próxima música da fila
async def play_next(ctx, guild_id):
    if queues[guild_id]:
        url, title = queues[guild_id].popleft()
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        try:
            source = discord.FFmpegPCMAudio(url, executable=FFMPEG_PATH, **ffmpeg_options)
        except Exception as e:
            await ctx.send(f"❌ Erro ao tocar: {title}\nPulando para a próxima...")
            await play_next(ctx, guild_id)
            return

        # Define o que acontece quando a música termina
        def after_playing(error, ctx=ctx, guild_id=guild_id):
            if error:
                print(f"[ERRO AO TOCAR]: {error}")
            fut = play_next(ctx, guild_id)
            asyncio.run_coroutine_threadsafe(fut, bot.loop)

        ctx.voice_client.play(source, after=partial(after_playing))
        await ctx.send(f"▶️ Tocando agora: **{title}**")
    else:
        await ctx.voice_client.disconnect()
        await ctx.send("📭 Fila finalizada. Saindo do canal.")

# Quando o bot estiver online
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user.name}")

# Comando para listar rádios disponíveis
@bot.command()
async def radios(ctx):
    lista = '\n'.join(f"• `{nome}`" for nome in RADIOS.keys())
    await ctx.send(f"📻 Rádios disponíveis:\n{lista}")

# !radio nome – toca uma rádio
@bot.command()
async def radio(ctx, station: str):
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

# !youtube URL ou nome – toca áudio do YouTube
@bot.command()
async def youtube(ctx, *, search):
    if ctx.author.voice is None:
        return await ctx.send("❌ Você precisa estar em um canal de voz.")

    voice_channel = ctx.author.voice.channel
    guild_id = ctx.guild.id

    # Cria fila para o servidor se ainda não existir
    if guild_id not in queues:
        queues[guild_id] = deque()

    # Extrai info do vídeo
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search, download=False)
            audio_url = info['url']
            title = info.get("title", "Desconhecido")

        # Adiciona à fila
        queues[guild_id].append((audio_url, title))
        await ctx.send(f"🎵 Adicionado à fila: **{title}**")

        # Conecta se não estiver conectado
        if ctx.voice_client is None or not ctx.voice_client.is_connected():
            await voice_channel.connect()

        # Se não estiver tocando nada, começa
        if not ctx.voice_client.is_playing():
            await play_next(ctx, guild_id)

    except Exception as e:
        await ctx.send("❌ Erro ao buscar o vídeo.")
        print(f"[ERRO YT] {e}")


@bot.command()
async def queue(ctx):
    guild_id = ctx.guild.id
    if guild_id not in queues or not queues[guild_id]:
        await ctx.send("📭 A fila está vazia.")
        return

    fila = list(queues[guild_id])
    resposta = '\n'.join([f"{i+1}. {titulo}" for i, (_, titulo) in enumerate(fila)])
    await ctx.send(f"📃 Fila atual:\n{resposta}")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Pulando para a próxima...")
    else:
        await ctx.send("❌ Nada está tocando.")

# !stop – para o áudio (mas continua no canal)
@bot.command()
async def stop(ctx):
    # Sempre limpa a fila
    if ctx.guild.id in queues:
        queues[ctx.guild.id].clear()

    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ Reprodução parada e fila limpa.")
    else:
        await ctx.send("🧹 Fila limpa. Nenhum áudio estava tocando.")

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
