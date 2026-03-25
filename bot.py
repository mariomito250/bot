import requests
import os
import time
import threading
import json
import random
import re
from flask import Flask

TOKEN = os.getenv("TOKEN")
ELEVEN_KEY = os.getenv("ELEVEN_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY")

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
# LIMPEZA TEXTO (IMPORTANTE PRA VOZ)
# =========================

def remover_emojis(texto):
    return re.sub(r'[^\w\s,.!?]', '', texto)

# =========================
# MOODS
# =========================

def detectar_mood(texto):
    texto = texto.lower()

    if any(p in texto for p in ["amo", "gosto", "te amo"]):
        return "feliz"
    if any(p in texto for p in ["odeio", "raiva", "idiota"]):
        return "brava"
    if any(p in texto for p in ["triste", "mal", "depressivo"]):
        return "triste"

    return "normal"

# =========================
# PERSONALIDADE
# =========================

def personalidade(texto, nome, mood):

    if mood == "feliz":
        return f"{nome}~ isso me deixa tão feliz!\n{texto}"

    if mood == "triste":
        return f"{nome}... não fica assim\n{texto}"

    if mood == "brava":
        return f"Hmph! {nome}...\n{texto}"

    return f"E-ei {nome}...\n{texto}"

# =========================
# GEMINI (ANTI-REPETIÇÃO)
# =========================

def perguntar_ia(user, texto):

    historico = memoria[user].get("historico", [])

    estilos = [
        "fofa e tímida",
        "brincalhona",
        "levemente ciumenta",
        "carinhosa",
        "provocante leve"
    ]

    contexto = "\n".join(historico[-4:])

    def gerar():

        estilo = random.choice(estilos)

        prompt = f"""
Você é uma garota anime.

REGRAS:
- Nunca repita respostas
- Seja curta
- Seja natural

Estilo: {estilo}

{contexto}

Usuário: {texto}
Resposta:
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 1.3,
                "topP": 0.95,
                "maxOutputTokens": 80
            }
        }

        r = requests.post(url, json=data)
        res = r.json()

        if "candidates" in res:
            return res["candidates"][0]["content"]["parts"][0]["text"].strip()

        return None

    for _ in range(3):

        resposta = gerar()

        if not resposta:
            continue

        if resposta != memoria[user].get("ultima_resposta"):

            memoria[user]["ultima_resposta"] = resposta

            historico.append(f"User: {texto}")
            historico.append(f"Bot: {resposta}")
            memoria[user]["historico"] = historico[-8:]

            return resposta

    return random.choice([
        "fala algo novo 😳",
        "não vou repetir 😤",
        "tenta diferente 😏"
    ])

# =========================
# VOZ (CORRIGIDA)
# =========================

def gerar_audio(texto):

    VOICE_ID = "ngvNHfiCrXLPAHcTrZK1"

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVEN_KEY,
        "Content-Type": "application/json"
    }

    texto_limpo = remover_emojis(texto).replace("\n", " ").strip()

    data = {
        "text": texto_limpo[:200],
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.9
        }
    }

    try:
        r = requests.post(url, json=data, headers=headers)

        print("AUDIO STATUS:", r.status_code)

        if r.status_code != 200:
            print("ERRO AUDIO:", r.text)
            return None

        if len(r.content) < 1000:
            print("AUDIO VAZIO")
            return None

        with open("voz.mp3", "wb") as f:
            f.write(r.content)

        return "voz.mp3"

    except Exception as e:
        print("ERRO VOZ:", e)
        return None

# =========================
# TELEGRAM
# =========================

def enviar_texto(chat, msg):
    requests.post(f"{BASE_URL}/sendMessage", data={
        "chat_id": chat,
        "text": msg
    })

def enviar_audio(chat, caminho):
    if caminho:
        with open(caminho, "rb") as f:
            requests.post(
                f"{BASE_URL}/sendVoice",
                files={"voice": f},
                data={"chat_id": chat}
            )

# =========================
# LOOP BOT
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
                        memoria[user] = {
                            "nome": "senpai",
                            "mood": "normal",
                            "historico": []
                        }

                    if "meu nome é" in texto.lower():
                        nome = texto.split("é")[-1].strip()
                        memoria[user]["nome"] = nome
                        salvar_memoria()
                        enviar_texto(chat, f"{nome}... gostei 💕")
                        continue

                    mood = detectar_mood(texto)
                    memoria[user]["mood"] = mood

                    resposta_base = perguntar_ia(user, texto)

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
    return "WAIFU ONLINE 💖"

print("Bot iniciando...")

iniciar()

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
