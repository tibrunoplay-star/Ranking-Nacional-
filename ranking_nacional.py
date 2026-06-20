import os
import requests
import psycopg
import discord
from bs4 import BeautifulSoup
from datetime import datetime
from discord.ext import commands, tasks

TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

CANAL_ID = 1517803367462604861

conn = psycopg.connect(DATABASE_URL)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Ligado como {bot.user}")

    try:
        atualizar_ranking.start()
        print("Task iniciada com sucesso")
    except Exception as e:
        print(f"Erro ao iniciar task: {e}")


@tasks.loop(minutes=30)
async def atualizar_ranking():
    print("Ranking nacional iniciado")
    # resto do código


@atualizar_ranking.before_loop
async def before_ranking():
    print("Bot pronto!")
    await bot.wait_until_ready()


agora = datetime.now()

ano = agora.year
mes = agora.month

url = (
    f"https://trucksbook.eu/company_stats/all/pt/"
    f"{ano}/{mes}/2/1/1"
)

try:

    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    texto = soup.get_text("\n")

    linhas = [
        l.strip()
        for l in texto.split("\n")
        if l.strip()
    ]

    # resto do código aqui...

except Exception as e:
    print(f"Erro ranking nacional: {e}")

bot.run(TOKEN)
