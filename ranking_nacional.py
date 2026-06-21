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
ULTIMA_MENSAGEM_ID = 1518190560551108779

conn = psycopg.connect(DATABASE_URL)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Ligado como {bot.user}")

    if not atualizar_ranking.is_running():
        atualizar_ranking.start()
        print("Task iniciada com sucesso")


@tasks.loop(minutes=30)
async def atualizar_ranking():

    print("Ranking nacional iniciado")

    agora = datetime.now()

    url = (
        f"https://trucksbook.eu/company_stats/all/pt/"
        f"{agora.year}/{agora.month}/2/1/1"
    )

    try:

        response = requests.get(
            url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        print(f"Status: {response.status_code}")

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        tabela = soup.find("table")

        if tabela is None:
            print("NENHUMA TABELA ENCONTRADA")
            return

        print("========== TABELA ==========")

        print(
            tabela.prettify()[:15000]
        )

        print("========== FIM ==========")

    except Exception as e:

        print(
            f"Erro ranking nacional: {e}"
        )

@atualizar_ranking.before_loop
async def before_ranking():
    print("Bot pronto!")
    await bot.wait_until_ready()


bot.run(TOKEN)

