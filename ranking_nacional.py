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
ULTIMA_MENSAGEM_ID =1518190560551108779
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

    canal = bot.get_channel(CANAL_ID)

    print(f"Canal encontrado: {canal}")

    if canal is None:
        print("ERRO: canal não encontrado")
        return

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

        print(f"Status: {response.status_code}")

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

        for i, linha in enumerate(linhas):

            if "VTC TRANS_BARBA" in linha:
            
               km_barba = linhas[i + 2]
               posicao = linhas[i + 4]

               mensagem = (
                   "🏆 Ranking Nacional TrucksBook 🇵🇹\n\n"
                   f"🚚 Empresa: VTC TRANS_BARBA\n"
                   f"🥈 Posição: {posicao}º\n"
                   f"📦 Quilómetros: {km_barba} km\n\n"
                   f"📅 Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
               )
               print(mensagem)

              global ULTIMA_MENSAGEM_ID

if ULTIMA_MENSAGEM_ID is None:

    msg = await canal.send(mensagem)
    ULTIMA_MENSAGEM_ID = msg.id

else:

    try:

        msg = await canal.fetch_message(
            ULTIMA_MENSAGEM_ID
        )

        await msg.edit(
            content=mensagem
        )

    except Exception:

        msg = await canal.send(
            mensagem
        )

        ULTIMA_MENSAGEM_ID = msg.id
               print("Mensagem enviada!")

               break

    except Exception as e:
        print(f"Erro ranking nacional: {e}")


@atualizar_ranking.before_loop
async def before_ranking():
    print("Bot pronto!")
    await bot.wait_until_ready()


bot.run(TOKEN)
