import requests
import random

# Substitua 'seu_token' pelo token real do seu bot
TOKEN = '6709271221:AAGmFdUjQ9g7Z-VquIVoRDc6xaZxagqphzw'
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'

# Lista de cores
cores = ['Vermelho', 'Azul', 'Verde', 'Amarelo', 'Roxo', 'Laranja', 'Preto', 'Branco']

# Lista de feitiços
magias = ['       𝙑𝙤𝙘𝙚̂ 𝙞𝙣𝙫𝙤𝙘𝙤𝙪 𝙪𝙢 𝙢𝙤𝙣𝙨𝙩𝙧𝙤 🧟‍♂ \n \n 💥 6 ᴅᴇ ᴅᴀɴᴏ 💥',
 '        𝙑𝙤𝙘𝙚‌ 𝙘𝙤𝙣𝙟𝙪𝙧𝙤𝙪 𝙪𝙢 𝙩𝙤𝙧𝙣𝙖𝙙𝙤🌪️ \n \n 💥 4 ᴅᴇ ᴅᴀɴᴏ 💥', 
 
 '          𝙑𝙤𝙘𝙚̂ 𝙜𝙖𝙣𝙝𝙤𝙪 𝙪𝙢 𝙥𝙚𝙩 🦊 \n \n ᴠᴏᴄᴇ̂ ᴄᴀᴜsᴀʀᴀ́ +2 ᴅᴇ ᴅᴀɴᴏ ᴀᴛᴇ́ ᴏ ғɪᴍ ᴅᴏ ᴊᴏɢᴏ', 
 
 '‎       ⚔ 𝘿𝙪𝙚𝙡𝙤 𝙙𝙚 𝙗𝙧𝙪𝙭𝙤𝙨 \n \n ⚔ ᴇsᴄᴏʟʜᴀ ᴜᴍ ᴀᴅᴠᴇʀsᴀ́ʀɪᴏ ᴘᴀʀᴀ ᴅᴜᴇʟᴀʀ ᴄᴏɴᴛʀᴀ ᴠᴏᴄᴇ̂', 
 
 ' ‎    ‎    𝙑𝙤𝙘𝙚̂ 𝙘𝙤𝙣𝙟𝙪𝙧𝙤𝙪 𝙪𝙢𝙖 𝙚𝙭𝙥𝙡𝙤𝙨𝙖̃𝙤 💥 \n \n ᴄᴀᴜsᴇ 2 ᴅᴇ ᴅᴀɴᴏ ᴇᴍ ᴛᴏᴅᴏs ᴏᴘᴏɴᴇɴᴛᴇs',
 
 '         𝙑𝙤𝙘𝙚̂ 𝙡𝙖𝙣𝙘̧𝙤𝙪 𝙪𝙢 𝙛𝙚𝙞𝙩𝙞𝙘̧𝙤 𝙙𝙚 𝙘𝙪𝙧𝙖 🌱 \n \n 🩸 +2 ᴅᴇ ᴠɪᴅᴀ 🩸',
 
 '          𝙑𝙤𝙘𝙚̂ 𝙘𝙤𝙣𝙟𝙪𝙧𝙤𝙪 𝙪𝙢 𝙧𝙖𝙞𝙤 ⚡️ \n \n    💥 2 ᴅᴇ ᴅᴀɴᴏ 💥',
 
' ‎           𝘼𝙣𝙩𝙞́𝙙𝙤𝙩𝙤 💊 \n \n   sᴇ ᴄᴜʀᴇ ᴅᴀ ᴘᴏᴄ̧ᴀ̃ᴏ ᴠᴇɴᴇɴᴏsᴀ',

'          ‎𝙑𝙤𝙘𝙚̂ 𝙘𝙤𝙣𝙟𝙪𝙧𝙤𝙪 𝙪𝙢𝙖 𝙥𝙤𝙘̧𝙖̃𝙤 𝙫𝙚𝙣𝙚𝙣𝙤𝙨𝙖 🧪 \n \n  sᴇᴜ ɪɴɪᴍɪɢᴏ sᴏғʀᴇʀᴀ́ 2 ᴅᴇ ᴅᴀɴᴏ ᴀᴏ ɪɴɪ́ᴄɪᴏ ᴅᴇ ᴛʀᴇ̂s ʀᴏᴅᴀᴅᴀs',

'          ‎        ‌‎𝘼𝙧𝙢𝙖 𝙢𝙖́𝙜𝙞𝙘𝙖 🪄 \n \n      ᴠᴏᴄᴇ̂ ᴄᴀᴜsᴀʀᴀ́ +1 ᴅᴇ ᴅᴀɴᴏ ᴀᴛᴇ́ ᴏ ғɪᴍ ᴅᴏ ᴊᴏɢᴏ',

'          ‎        ‎𝘾𝙖𝙥𝙖 𝙙𝙖 𝙞𝙣𝙫𝙞𝙨𝙞𝙗𝙞𝙡𝙞𝙙𝙖𝙙𝙚 \n \n    ғɪǫᴜᴇ ᴘʀᴏᴛᴇɢɪᴅᴏ ᴘᴏʀ ᴜᴍᴀ ʀᴏᴅᴀᴅᴀ'] 

# Função para enviar uma mensagem
def enviar_mensagem(chat_id, mensagem, reply_to_message_id=None):
    url = f'{BASE_URL}/sendMessage'
    params = {'chat_id': chat_id, 'text': mensagem, 'reply_to_message_id': reply_to_message_id}
    requests.post(url, params=params)

# Função para o comando /cores
def comando_cor(chat_id, message_id):
    cor_aleatoria = random.choice(cores)
    mensagem_resposta = f'{cor_aleatoria}'
    enviar_mensagem(chat_id, mensagem_resposta, reply_to_message_id=message_id)

# Função para o comando /magia
def comando_magia(chat_id, message_id):
    magia_aleatoria = random.choice(magias)
    mensagem_resposta = f'{magia_aleatoria}'
    enviar_mensagem(chat_id, mensagem_resposta, reply_to_message_id=message_id)

# Função principal para obter atualizações e processar mensagens
def main():
    offset = None

    while True:
        # Obter atualizações
        url = f'{BASE_URL}/getUpdates'
        params = {'offset': offset, 'timeout': 30}
        response = requests.get(url, params=params).json()

        # Processar cada atualização
        for update in response.get('result', []):
            offset = update['update_id'] + 1
            message = update.get('message')

            if message and 'text' in message:
                text = message['text']

                # Verificar se a mensagem é um comando
                if text.startswith('/cores'):
                    comando_cor(message['chat']['id'], message['message_id'])
                elif text.startswith('/magia'):
                    comando_magia(message['chat']['id'], message['message_id'])
                else:
                    # Responder a mensagens não reconhecidas
                    enviar_mensagem(message['chat']['id'], 'Não entendi. Tente /ajuda para ver os comandos existentes.', reply_to_message_id=message['message_id'])

# Bot iniciado
print("Bot Iniciado Com Sucesso")

if __name__ == '__main__':
    main()