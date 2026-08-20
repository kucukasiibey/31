import os
import asyncio
import nest_asyncio
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import WebsocketError, SessionClosedError

nest_asyncio.apply()

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

token = "ad40c52f78abc4a1a510efa2bd827e47e3af4d42"
character_id = "hBH_mAY7JFcX8nBIdabIs5ixJ2uW6rTdMRMfs1wAi-E"

client = None
chat_id = None
loop = asyncio.get_event_loop()


async def connect():
    global client, chat_id
    client = await get_client(token=token)
    chat, greeting = await client.chat.create_chat(character_id)
    chat_id = chat.chat_id
    print(f"[INIT] Yeni sohbet açıldı: {chat_id}")


async def send(user_message):
    global client, chat_id
    try:
        answer = await client.chat.send_message(character_id, chat_id, user_message)
        return answer.get_primary_candidate().text
    except (WebsocketError, SessionClosedError):
        print("[RECONNECT] Bağlantı koptu, yeniden bağlanılıyor...")
        await connect()
        answer = await client.chat.send_message(character_id, chat_id, user_message)
        return answer.get_primary_candidate().text


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/mesaj", methods=["POST"])
def mesaj():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Mesaj bulunamadı"}), 400

    user_message = data["message"]

    try:
        reply = loop.run_until_complete(send(user_message))
    except Exception as e:
        return jsonify({"error": f"Bot hatası: {str(e)}"}), 500

    return jsonify({"reply": reply, "chat_id": chat_id})


@app.route("/reset", methods=["POST"])
def reset():
    try:
        loop.run_until_complete(connect())
    except Exception as e:
        return jsonify({"error": f"Reset hatası: {str(e)}"}), 500

    return jsonify({"status": "ok", "chat_id": chat_id})


if __name__ == "__main__":
    loop.run_until_complete(connect())
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
