import requests
import random
import json
import threading
import os
import time
from flask import Flask

TOKEN = "6709271221:AAEB6gpH_HN0UYhGV2shXa0mvc6HQc8Gi9A"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

players = {}

# =========================
# salvar jogadores
# =========================

def salvar():
    with open("players.json","w") as f:
        json.dump(players,f)

def carregar():
    global players
    try:
        with open("players.json") as f:
            players=json.load(f)
    except:
        players={}

carregar()

# =========================
# enviar mensagem
# =========================

def enviar(chat,msg,reply=None):

    url=f"{BASE_URL}/sendMessage"

    data={
        "chat_id":chat,
        "text":msg
    }

    if reply:
        data["reply_to_message_id"]=reply

    try:
        requests.post(url,data=data)
    except:
        pass

# =========================
# criar personagem
# =========================

def criar(user,nome):

    if str(user) not in players:

        players[str(user)]={
            "nome":nome,
            "vida":30,
            "maxvida":30,
            "atk":5,
            "ouro":10,
            "xp":0,
            "level":1,
            "pocoes":1
        }

        salvar()

        return "🧙 Personagem criado!"

    return "Você já possui personagem."

# =========================
# status
# =========================

def status(user):

    p=players[str(user)]

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

    p=players[str(user)]

    eventos=["monstro","ouro","pocao","nada"]

    e=random.choice(eventos)

    if e=="monstro":

        dano=random.randint(2,6)

        p["vida"]-=dano
        p["xp"]+=5

        salvar()

        return f"👹 Monstro apareceu!\n💥 perdeu {dano} vida"

    if e=="ouro":

        g=random.randint(5,15)

        p["ouro"]+=g
        salvar()

        return f"💰 encontrou {g} ouro"

    if e=="pocao":

        p["pocoes"]+=1
        salvar()

        return "🧪 encontrou uma poção"

    return "🌳 nada aconteceu"

# =========================
# usar poção
# =========================

def curar(user):

    p=players[str(user)]

    if p["pocoes"]<=0:
        return "❌ você não tem poções"

    p["pocoes"]-=1

    p["vida"]+=10

    if p["vida"]>p["maxvida"]:
        p["vida"]=p["maxvida"]

    salvar()

    return "🧪 você usou uma poção"

# =========================
# ranking
# =========================

def ranking():

    lista=sorted(players.items(),key=lambda x:x[1]["level"],reverse=True)

    txt="🏆 Ranking\n\n"

    for i,p in enumerate(lista[:10]):
        txt+=f"{i+1}. {p[1]['nome']} lvl {p[1]['level']}\n"

    return txt

# =========================
# bot loop
# =========================

def bot():

    offset=None

    while True:

        try:

            url=f"{BASE_URL}/getUpdates"

            params={"offset":offset,"timeout":30}

            r=requests.get(url,params=params).json()

            if "result" not in r:
                print("Erro API:",r)
                time.sleep(2)
                continue

            for up in r["result"]:

                offset=up["update_id"]+1

                msg=up.get("message")

                if not msg:
                    continue

                text=msg.get("text","")

                user=msg["from"]["id"]
                nome=msg["from"]["first_name"]
                chat=msg["chat"]["id"]
                mid=msg["message_id"]

                if text=="/start":

                    enviar(chat,criar(user,nome),mid)

                elif text=="/status":

                    if str(user) in players:
                        enviar(chat,status(user),mid)

                elif text=="/explorar":

                    if str(user) in players:
                        enviar(chat,explorar(user),mid)

                elif text=="/pocao":

                    if str(user) in players:
                        enviar(chat,curar(user),mid)

                elif text=="/ranking":

                    enviar(chat,ranking(),mid)

        except Exception as e:

            print("Erro no bot:",e)
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

port = int(os.environ.get("PORT",10000))
app.run(host="0.0.0.0",port=port)