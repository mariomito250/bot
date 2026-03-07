import requests
import random
import json
import threading
from flask import Flask

TOKEN = "6709271221:AAEB6gpH_HN0UYhGV2shXa0mvc6HQc8Gi9A"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

players = {}
boss = {"vida":100}

# =====================
# salvar dados
# =====================

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

# =====================
# enviar mensagem
# =====================

def enviar(chat,msg,reply=None):

    url=f"{BASE_URL}/sendMessage"

    data={
        "chat_id":chat,
        "text":msg
    }

    if reply:
        data["reply_to_message_id"]=reply

    requests.post(url,data=data)

# =====================
# criar player
# =====================

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

# =====================
# level up
# =====================

def levelup(p):

    if p["xp"]>=20:

        p["xp"]=0
        p["level"]+=1
        p["atk"]+=2
        p["maxvida"]+=5
        p["vida"]=p["maxvida"]

        return True

    return False

# =====================
# status
# =====================

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

# =====================
# atacar
# =====================

def atacar(atk,alvo):

    dano=random.randint(1,players[str(atk)]["atk"])

    players[str(alvo)]["vida"]-=dano

    players[str(atk)]["xp"]+=3

    salvar()

    return f"⚔ Ataque causou {dano} de dano!"

# =====================
# magia
# =====================

magias=[
("🔥 Bola de fogo",6),
("⚡ Raio",5),
("❄ Gelo",4)
]

def magia(alvo):

    m=random.choice(magias)

    nome=m[0]
    dano=m[1]

    players[str(alvo)]["vida"]-=dano

    salvar()

    return f"{nome} causou {dano} de dano!"

# =====================
# explorar
# =====================

def explorar(user):

    p=players[str(user)]

    eventos=[
        "monstro",
        "ouro",
        "pocao",
        "nada"
    ]

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

        return f"💰 achou {g} ouro"

    if e=="pocao":

        p["pocoes"]+=1
        salvar()

        return "🧪 encontrou uma poção"

    return "🌳 nada aconteceu"

# =====================
# usar poção
# =====================

def curar(user):

    p=players[str(user)]

    if p["pocoes"]<=0:
        return "❌ você não tem poções"

    p["vida"]+=10

    if p["vida"]>p["maxvida"]:
        p["vida"]=p["maxvida"]

    p["pocoes"]-=1

    salvar()

    return "🧪 você usou uma poção"

# =====================
# boss
# =====================

def atacar_boss(user):

    global boss

    p=players[str(user)]

    dano=random.randint(2,p["atk"])

    boss["vida"]-=dano

    p["xp"]+=5

    salvar()

    if boss["vida"]<=0:

        boss["vida"]=100

        p["ouro"]+=50

        return "🐉 Boss derrotado! ganhou 50 ouro!"

    return f"⚔ causou {dano} no boss\n🐉 vida boss {boss['vida']}"

# =====================
# ranking
# =====================

def ranking():

    lista=sorted(players.items(),key=lambda x:x[1]["level"],reverse=True)

    txt="🏆 Ranking\n\n"

    for i,p in enumerate(lista[:10]):

        txt+=f"{i+1}. {p[1]['nome']} lvl {p[1]['level']}\n"

    return txt

# =====================
# loop bot
# =====================

def bot():

    offset=None

    while True:

        url=f"{BASE_URL}/getUpdates"

        params={"offset":offset,"timeout":30}

        r=requests.get(url,params=params).json()

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

                enviar(chat,explorar(user),mid)

            elif text=="/pocao":

                enviar(chat,curar(user),mid)

            elif text=="/boss":

                enviar(chat,atacar_boss(user),mid)

            elif text=="/ranking":

                enviar(chat,ranking(),mid)

            elif text=="/atacar":

                if msg.get("reply_to_message"):

                    alvo=msg["reply_to_message"]["from"]["id"]

                    if str(alvo) in players:

                        enviar(chat,atacar(user,alvo),mid)

            elif text=="/magia":

                if msg.get("reply_to_message"):

                    alvo=msg["reply_to_message"]["from"]["id"]

                    if str(alvo) in players:

                        enviar(chat,magia(alvo),mid)

# =====================
# iniciar bot
# =====================

def iniciar():

    threading.Thread(target=bot).start()

# =====================
# web server
# =====================

@app.route("/")
def home():
    return "RPG BOT ONLINE"

print("RPG BOT ONLINE")

iniciar()

app.run(host="0.0.0.0",port=10000)