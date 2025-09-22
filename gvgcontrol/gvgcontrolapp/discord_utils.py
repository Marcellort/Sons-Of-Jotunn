
import requests

import os
from dotenv import load_dotenv
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')


def send_discord_message(discord_id, message):
    """
    Envia uma DM para o usuário Discord usando a API REST (requests), igual ao curl.
    """
    try:
        # 1. Cria canal DM
        r = requests.post(
            'https://discord.com/api/v10/users/@me/channels',
            headers={
                'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
                'Content-Type': 'application/json'
            },
            json={"recipient_id": str(discord_id)}
        )
        r.raise_for_status()
        channel_id = r.json()["id"]
        # 2. Envia mensagem
        r2 = requests.post(
            f'https://discord.com/api/v10/channels/{channel_id}/messages',
            headers={
                'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
                'Content-Type': 'application/json'
            },
            json={"content": message}
        )
        r2.raise_for_status()
        return True, None
    except Exception as e:
        return False, str(e)
