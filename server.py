import os
import asyncio
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PyCharacterAI import get_client

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

token = "ad40c52f78abc4a1a510efa2bd827e47e3af4d42"

print("Token bulundu mu?", token is not None)
character_id = "hBH_mAY7JFcX8nBIdabIs5ixJ2uW6rTdMRMfs1wAi-E"

client = None
chat_id = None


async def init_client():
    global client, chat_id

    client = await get_client(token=token)
    chat, greeting = await client.chat.create_chat(character_id)
    chat_id = chat.chat_id


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/mesaj", methods=["POST"])
def mesaj():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Mesaj bulunamadı"}), 400

    user_message = data["message"]

    async def get_reply():
        answer = await client.chat.send_message(
            character_id,
            chat_id,
            user_message
        )
        return answer.get_primary_candidate().text

    reply = asyncio.run(get_reply())

    return jsonify({
        "reply": reply
    })


if __name__ == "__main__":
    asyncio.run(init_client())

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
