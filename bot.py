import requests
import os
import time
import threading
import json
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
        return f"{nome}~ isso me deixa tão feliz! 💕\n{texto}"

    if mood == "triste":
        return f"{nome}... não fica assim 😢\n{texto}"

    if mood == "brava":
        return f"Hmph! {nome}... você é impossível 😤\n{texto}"

    return f"E-ei {nome}...\n{texto} >///<"

# =========================
# IA GEMINI (CORRIGIDA)
# =========================

def perguntar_ia(user, texto):

    historico = memoria[user].get("historico", [])

    contexto = ""
    for h in historico[-4:]:
        contexto += f"{h}\n"

    prompt = f"""
Você é uma garota anime (waifu), fofa, levemente ciumenta e divertida.
Responda de forma natural, curta e variada. Nunca repita frases.

{contexto}
Usuário: {texto}
Waifu:
"""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

        data = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        r = requests.post(url, json=data)
        res = r.json()

        print("DEBUG GEMINI:", res)

        # ✅ parser seguro
        if "candidates" in res and len(res["candidates"]) > 0:
            parts = res["candidates"][0].get("content", {}).get("parts", [])
            if len(parts) > 0 and "text" in parts[0]:
                resposta = parts[0]["text"].strip()
            else:
                return "E-eh? fala melhor comigo... 😖"
        else:
            return "Hmm... tenta de novo 😢"

        # 🚫 evitar repetição
        if resposta == memoria[user].get("ultima_resposta"):
            return "Você tá me testando? 😤 fala outra coisa..."

        memoria[user]["ultima_resposta"] = resposta

        # 🧠 salvar histórico
        historico.append(f"Usuário: {texto}")
        historico.append(f"Waifu: {resposta}")
        memoria[user]["historico"] = historico[-8:]

        return resposta

    except Exception as e:
        print("ERRO GEMINI:", e)
        return "Deu bug aqui 😵"

# =========================
# VOZ
# =========================

def gerar_audio(texto):

    VOICE_ID = "ngvNHfiCrXLPAHcTrZK1"

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVEN_KEY,
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

    try:
        r = requests.post(url, json=data, headers=headers)

        with open("voz.mp3", "wb") as f:
            f.write(r.content)

        return "voz.mp3"
    except:
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
                        memoria[user] = {
                            "nome": "senpai",
                            "mood": "normal",
                            "historico": []
                        }

                    # aprender nome
                    if "meu nome é" in texto.lower():
                        nome = texto.split("é")[-1].strip()
                        memoria[user]["nome"] = nome
                        salvar_memoria()
                        enviar_texto(chat, f"Aaah! {nome} 💕")
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
    return "WAIFU GEMINI 💖"

print("Waifu GOD (Gemini) iniciando...")

iniciar()

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
