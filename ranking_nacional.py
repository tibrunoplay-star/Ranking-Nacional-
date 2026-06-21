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

    global ULTIMA_MENSAGEM_ID

    print("Ranking nacional iniciado")

    canal = bot.get_channel(CANAL_ID)

    if canal is None:
        print("Canal não encontrado")
        return

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

        texto = soup.get_text("\n")

        linhas = [
            l.strip()
            for l in texto.split("\n")
            if l.strip()
        ]

       # DEBUG TABELA HTML

       tabela = soup.find("table")

       if tabela is None:

           print("❌ Nenhuma tabela encontrada")

       else:

            print("========== TABELA ENCONTRADA ==========")

            print(
                 tabela.prettify()[:5000]
            )

            print("======================================")
        ranking = []

        for i, linha in enumerate(linhas):

            try:

                if linha.startswith("VTC"):

                    km = int(
                        linhas[i + 2].replace(" ", "")
                    )

                    ranking.append({
                        "nome": linha,
                        "km": km
                    })

            except:
                pass

        if len(ranking) == 0:
            print("Nenhuma empresa encontrada")
            return

        ranking.sort(
            key=lambda x: x["km"],
            reverse=True
        )

        trans_barba = None

        for posicao, empresa in enumerate(
            ranking,
            start=1
        ):

            if "TRANS_BARBA" in empresa["nome"]:

                trans_barba = {
                    "posicao": posicao,
                    "nome": empresa["nome"],
                    "km": empresa["km"]
                }

                break

        if trans_barba is None:
            print("TRANS_BARBA não encontrada")
            return

        lider = ranking[0]

        diferenca = (
            lider["km"]
            - trans_barba["km"]
        )

        mensagem = (
            "🏆 Ranking Nacional TrucksBook 🇵🇹\n\n"
        )

        for posicao, empresa in enumerate(
            ranking[:10],
            start=1
        ):

            if posicao == 1:
                emoji = "🥇"
            elif posicao == 2:
                emoji = "🥈"
            elif posicao == 3:
                emoji = "🥉"
            else:
                emoji = "🔹"

            mensagem += (
                f"{emoji} {posicao}º "
                f"{empresa['nome']} — "
                f"{empresa['km']:,} km\n"
            )

        mensagem += (
            "\n"
            f"🚚 {trans_barba['nome']}\n"
            f"🏅 Posição: {trans_barba['posicao']}º\n"
            f"📦 Quilómetros: {trans_barba['km']:,} km\n"
            f"📉 Diferença para o líder: {diferenca:,} km\n\n"
            f"📅 Atualizado: "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )

        mensagem = mensagem.replace(",", ".")

        try:

            msg = await canal.fetch_message(
                ULTIMA_MENSAGEM_ID
            )

            await msg.edit(
                content=mensagem
            )

            print("Mensagem editada")

        except Exception:

            msg = await canal.send(
                mensagem
            )

            ULTIMA_MENSAGEM_ID = msg.id

            print("Nova mensagem enviada")

    except Exception as e:

        print(
            f"Erro ranking nacional: {e}"
        )


@atualizar_ranking.before_loop
async def before_ranking():
    print("Bot pronto!")
    await bot.wait_until_ready()


bot.run(TOKEN)

