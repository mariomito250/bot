import requests
import random
import threading
import time
from flask import Flask

TOKEN = "SEU_TOKEN_AQUI"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

cores = ['Vermelho','Azul','Verde','Amarelo','Roxo','Laranja','Preto','Branco']

magias = [
"Você invocou um monstro 🧟‍♂\n\n💥 6 de dano 💥",
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
        url = f"{BASE_URL}/getUpdates"
        params = {"offset": offset, "timeout": 30}

        response = requests.get(url, params=params).json()

        for update in response.get("result", []):
            offset = update["update_id"] + 1
            message = update.get("message")

            if message and "text" in message:
                text = message["text"]

                if text.startswith("/cores"):
                    comando_cor(message["chat"]["id"], message["message_id"])

                elif text.startswith("/magia"):
                    comando_magia(message["chat"]["id"], message["message_id"])

def iniciar_bot():
    threading.Thread(target=bot).start()

@app.route("/")
def home():
    return "Bot rodando!"

print("Bot iniciado")

iniciar_bot()

app.run(host="0.0.0.0", port=10000)