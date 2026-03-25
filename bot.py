import requests
import os
import time
import threading
import json
from flask import Flask

TOKEN = os.getenv("TOKEN")
ELEVEN_KEY = os.getenv("ELEVEN_KEY")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# =========================
# MEMORIA
# =========================

def carregar_memoria():
    try:
        with open("memoria.json") as f:
            return json.load(f)
    except:
        return {}

def salvar_memoria():
    with open("memoria.json", "w") as f:
        json.dump(memoria, f)

memoria = carregar_memoria()

# =========================
# MOODS
# =========================

def detectar_mood(texto):

    texto = texto.lower()

    if "amo" in texto or "gosto" in texto:
        return "feliz"
    if "odeio" in texto or "raiva" in texto:
        return "brava"
    if "triste" in texto:
        return "triste"

    return "normal"

# =========================
# PERSONALIDADE
# =========================

def personalidade(texto, nome, mood):

    if mood == "feliz":
        return f"{nome}~ isso me deixa tão feliz! 💕 {texto}"

    if mood == "triste":
        return f"{nome}... não fica assim 😢 {texto}"

    if mood == "brava":
        return f"Hmph! {nome}... você é impossível 😤 {texto}"

    return f"E-ei {nome}... {texto} >///<"

# =========================
# IA (HuggingFace)
# =========================

API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

def perguntar_ia(texto):

    try:
        r = requests.post(API_URL, json={"inputs": texto})
        return r.json()[0]["generated_text"]
    except:
        return "Não entendi muito bem..."

# =========================
# VOZ REALISTA (ElevenLabs)
# =========================

def gerar_audio(texto):

    VOICE_ID = "ngvNHfiCrXLPAHcTrZK1"

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": os.getenv("ELEVEN_KEY"),
        "Content-Type": "application/json"
    }

    data = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.3,
            "similarity_boost": 0.9
        }
    }

    r = requests.post(url, json=data, headers=headers)

    with open("voz.mp3", "wb") as f:
        f.write(r.content)

    return "voz.mp3"

# =========================
# TELEGRAM
# =========================

def enviar_texto(chat, msg):
    requests.post(f"{BASE_URL}/sendMessage", data={
        "chat_id": chat,
        "text": msg
    })

def enviar_audio(chat, caminho):
    with open(caminho, "rb") as f:
        requests.post(f"{BASE_URL}/sendVoice",
        files={"voice": f},
        data={"chat_id": chat})

# =========================
# BOT LOOP
# =========================

def bot():

    offset = None

    while True:

        try:

            r = requests.get(f"{BASE_URL}/getUpdates", params={
                "offset": offset,
                "timeout": 30
            }).json()

            for up in r.get("result", []):

                offset = up["update_id"] + 1

                msg = up.get("message", {})
                chat = msg.get("chat", {}).get("id")
                user = str(msg.get("from", {}).get("id"))

                if "text" in msg:

                    texto = msg["text"]

                    if user not in memoria:
                        memoria[user] = {"nome": "senpai", "mood": "normal"}

                    # aprender nome
                    if "meu nome é" in texto.lower():
                        nome = texto.split("é")[-1].strip()
                        memoria[user]["nome"] = nome
                        salvar_memoria()
                        enviar_texto(chat, f"Aaah! {nome} 💕")
                        continue

                    mood = detectar_mood(texto)
                    memoria[user]["mood"] = mood

                    resposta_base = perguntar_ia(texto)

                    resposta = personalidade(
                        resposta_base,
                        memoria[user]["nome"],
                        mood
                    )

                    salvar_memoria()

                    enviar_texto(chat, resposta)

                    audio = gerar_audio(resposta)
                    enviar_audio(chat, audio)

        except Exception as e:
            print("Erro:", e)
            time.sleep(3)

# =========================
# START
# =========================

def iniciar():
    threading.Thread(target=bot).start()

@app.route("/")
def home():
    return "WAIFU GOD MODE 💖"

print("Waifu GOD iniciando...")

iniciar()

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
