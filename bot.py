import requests
import random
import threading
import time
import os
from flask import Flask

TOKEN = "6709271221:AAEB6gpH_HN0UYhGV2shXa0mvc6HQc8Gi9A"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

cores = [
'Vermelho','Azul','Verde','Amarelo','Roxo',
'Laranja','Preto','Branco'
]

magias = [
"Você invocou um monstro 🧟‍♂️\n\n💥 6 de dano 💥",
"Você conjurou um tornado 🌪️\n\n💥 4 de dano 💥",
"Você ganhou um pet 🦊\n\n+2 de dano até o fim do jogo"
]

def enviar_mensagem(chat_id, mensagem, reply_to_message_id=None):
    url = f"{BASE_URL}/sendMessage"

    params = {
        "chat_id": chat_id,
        "text": mensagem,
        "reply_to_message_id": reply_to_message_id
    }

    requests.post(url, params=params)


def comando_cor(chat_id, message_id):
    enviar_mensagem(chat_id, random.choice(cores), message_id)


def comando_magia(chat_id, message_id):
    enviar_mensagem(chat_id, random.choice(magias), message_id)


def bot():

    offset = None

    while True:
        try:

            url = f"{BASE_URL}/getUpdates"
            params = {"offset": offset, "timeout": 30}

            response = requests.get(url, params=params).json()

            for update in response.get("result", []):

                offset = update["update_id"] + 1
                message = update.get("message")

                if message and "text" in message:

                    text = message["text"]
                    chat_id = message["chat"]["id"]
                    message_id = message["message_id"]

                    print("Mensagem recebida:", text)

                    if text.startswith("/cores"):
                        comando_cor(chat_id, message_id)

                    elif text.startswith("/magia"):
                        comando_magia(chat_id, message_id)

        except Exception as e:
            print("Erro:", e)

        time.sleep(1)


def iniciar_bot():
    threading.Thread(target=bot).start()


@app.route("/")
def home():
    return "Bot rodando!"


print("Bot iniciado")

iniciar_bot()

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)