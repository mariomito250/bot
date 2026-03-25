import requests
import random
import json
import threading
import os
import time
from flask import Flask

TOKEN = os.getenv("TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

players = {}

# =========================
# salvar jogadores
# =========================

def salvar():
    with open("players.json", "w") as f:
        json.dump(players, f)

def carregar():
    global players
    try:
        with open("players.json") as f:
            players = json.load(f)
    except:
        players = {}

carregar()

# =========================
# enviar mensagem
# =========================

def enviar(chat, msg, reply=None):
    url = f"{BASE_URL}/sendMessage"

    data = {
        "chat_id": chat,
        "text": msg
    }

    if reply:
        data["reply_to_message_id"] = reply

    try:
        requests.post(url, data=data)
    except:
        pass

# =========================
# verificar player
# =========================

def check_player(user):
    return str(user) in players

# =========================
# criar personagem
# =========================

def criar(user, nome):

    if not check_player(user):

        players[str(user)] = {
            "nome": nome,
            "vida": 30,
            "maxvida": 30,
            "atk": 5,
            "ouro": 10,
            "xp": 0,
            "level": 1,
            "pocoes": 1
        }

        salvar()

        return "🧙 Personagem criado!"

    return "⚠️ Você já possui personagem."

# =========================
# level up
# =========================

def verificar_level(p):

    xp_need = p["level"] * 10

    if p["xp"] >= xp_need:
        p["xp"] = 0
        p["level"] += 1
        p["maxvida"] += 5
        p["atk"] += 2
        p["vida"] = p["maxvida"]

        return f"🎉 LEVEL UP!\nAgora você é level {p['level']}"

    return None

# =========================
# status
# =========================

def status(user):

    p = players[str(user)]

    return f"""
🧙 {p['nome']}

❤️ Vida {p['vida']}/{p['maxvida']}
⚔ Ataque {p['atk']}
⭐ XP {p['xp']}
💰 Ouro {p['ouro']}
🧪 Poções {p['pocoes']}
🏅 Level {p['level']}
"""

# =========================
# explorar
# =========================

def explorar(user):

    p = players[str(user)]

    if p["vida"] <= 0:
        return "💀 Você está morto! Use /reviver"

    eventos = ["monstro", "ouro", "pocao", "nada"]

    e = random.choice(eventos)

    if e == "monstro":

        dano = random.randint(2, 6)

        p["vida"] -= dano
        p["xp"] += 5

        if p["vida"] <= 0:
            p["vida"] = 0
            salvar()
            return "💀 Você morreu em batalha!"

        lvl = verificar_level(p)

        salvar()

        return f"👹 Monstro!\n💥 perdeu {dano} vida\n{lvl if lvl else ''}"

    if e == "ouro":

        g = random.randint(5, 15)

        p["ouro"] += g
        salvar()

        return f"💰 encontrou {g} ouro"

    if e == "pocao":

        p["pocoes"] += 1
        salvar()

        return "🧪 encontrou uma poção"

    return "🌳 nada aconteceu"

# =========================
# usar poção
# =========================

def curar(user):

    p = players[str(user)]

    if p["vida"] <= 0:
        return "💀 Você está morto!"

    if p["pocoes"] <= 0:
        return "❌ Sem poções"

    p["pocoes"] -= 1
    p["vida"] += 10

    if p["vida"] > p["maxvida"]:
        p["vida"] = p["maxvida"]

    salvar()

    return "🧪 curado +10 vida"

# =========================
# reviver
# =========================

def reviver(user):

    p = players[str(user)]

    if p["vida"] > 0:
        return "⚠️ Você não está morto"

    p["vida"] = p["maxvida"] // 2

    salvar()

    return "✨ Você reviveu!"

# =========================
# loja
# =========================

def loja(user):

    p = players[str(user)]

    if p["ouro"] < 10:
        return "❌ Ouro insuficiente"

    p["ouro"] -= 10
    p["pocoes"] += 1

    salvar()

    return "🛒 Comprou 1 poção por 10 ouro"

# =========================
# ranking
# =========================

def ranking():

    lista = sorted(players.items(), key=lambda x: x[1]["level"], reverse=True)

    txt = "🏆 Ranking\n\n"

    for i, p in enumerate(lista[:10]):
        txt += f"{i+1}. {p[1]['nome']} lvl {p[1]['level']}\n"

    return txt

# =========================
# bot loop
# =========================

def bot():

    offset = None

    while True:

        try:

            url = f"{BASE_URL}/getUpdates"
            params = {"offset": offset, "timeout": 30}

            r = requests.get(url, params=params).json()

            if "result" not in r:
                time.sleep(2)
                continue

            for up in r["result"]:

                offset = up["update_id"] + 1

                msg = up.get("message")

                if not msg:
                    continue

                text = msg.get("text", "")
                user = msg["from"]["id"]
                nome = msg["from"]["first_name"]
                chat = msg["chat"]["id"]
                mid = msg["message_id"]

                # START
                if text == "/start":
                    enviar(chat, criar(user, nome), mid)
                    continue

                # CHECK PLAYER
                if not check_player(user):
                    enviar(chat, "❌ Use /start primeiro", mid)
                    continue

                # COMANDOS
                if text == "/status":
                    enviar(chat, status(user), mid)

                elif text == "/explorar":
                    enviar(chat, explorar(user), mid)

                elif text == "/pocao":
                    enviar(chat, curar(user), mid)

                elif text == "/reviver":
                    enviar(chat, reviver(user), mid)

                elif text == "/loja":
                    enviar(chat, loja(user), mid)

                elif text == "/ranking":
                    enviar(chat, ranking(), mid)

        except Exception as e:
            print("Erro:", e)
            time.sleep(3)

# =========================
# iniciar bot
# =========================

def iniciar():
    threading.Thread(target=bot).start()

# =========================
# servidor web
# =========================

@app.route("/")
def home():
    return "BOT ONLINE"

print("Bot iniciado")

iniciar()

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
