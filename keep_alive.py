from flask import Flask
from threading import Thread

app = Flask(__name__)


@app.route("/")
def home():
    return "<h1>🌸 Alya Bot is alive!</h1><p>Cute but powerful 💖</p>"


@app.route("/health")
def health():
    return {"status": "ok", "bot": "Alya"}, 200


def run():
    app.run(host="0.0.0.0", port=9000)


def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
