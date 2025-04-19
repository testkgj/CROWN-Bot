from flask import Flask
import threading
import os

app = Flask('')

# Route de base pour vérifier si le serveur est actif
@app.route('/')
def home():
    return "Le serveur est en ligne !"

# Fonction pour démarrer le serveur Flask
def run():
    app.run(host='0.0.0.0', port=8080)

# Démarre le serveur Flask dans un thread séparé
def keep_alive():
    t = threading.Thread(target=run)
    t.start()

if __name__ == '__main__':
    keep_alive()
