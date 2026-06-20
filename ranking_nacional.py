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
    atualizar_ranking.start()

@tasks.loop(minutes=30)
async def atualizar_ranking():


canal = bot.get_channel(CANAL_ID)

if canal is None:
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
        headers={
            "User-Agent":
            "Mozilla/5.0"
        }
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

    top = []
    trans_pos = None
    trans_km = None

    for i, linha in enumerate(linhas):

        if (
            "TRANS VELOZ" in linha
            or "TRANS_BARBA" in linha
            or "VLP" in linha
        ):

            top.append(linha)

        if "TRANS_BARBA" in linha:

            trans_pos = len(top)

    mensagem_texto = (
        "🏆 RANKING NACIONAL TRUCKSBOOK 🇵🇹\n\n"
    )

    for i, empresa in enumerate(
        top[:3],
        start=1
    ):

        medalha = ["🥇", "🥈", "🥉"][i-1]

        mensagem_texto += (
            f"{medalha} {empresa}\n"
        )

    mensagem_texto += (
        "\n━━━━━━━━━━━━━━━━━━\n\n"
        "🚚 VTC TRANS_BARBA\n\n"
    )

    if trans_pos:
        mensagem_texto += (
            f"📍 Posição Nacional: "
            f"{trans_pos}º\n"
        )

    mensagem_texto += (
        f"\n🕒 Atualizado: "
        f"{agora.strftime('%d/%m/%Y %H:%M')}"
    )

    with conn.cursor() as cur:

        cur.execute("""
            SELECT mensagem_id
            FROM ranking_nacional_msg
            LIMIT 1
        """)

        resultado = cur.fetchone()

        if resultado is None:

            msg = await canal.send(
                mensagem_texto
            )

            cur.execute("""
                INSERT INTO ranking_nacional_msg
                (mensagem_id)
                VALUES (%s)
            """, (msg.id,))

            conn.commit()

        else:

            mensagem_id = resultado[0]

            try:

                msg = await canal.fetch_message(
                    mensagem_id
                )

                await msg.edit(
                    content=mensagem_texto
                )

            except:

                msg = await canal.send(
                    mensagem_texto
                )

                cur.execute("""
                    UPDATE ranking_nacional_msg
                    SET mensagem_id=%s
                """, (msg.id,))

                conn.commit()

except Exception as e:
    print(
        f"Erro ranking nacional: {e}"
    )
```

bot.run(TOKEN)
