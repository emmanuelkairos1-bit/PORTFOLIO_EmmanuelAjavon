"""
Serveur de production du portfolio d'Emmanuel Ajavon.

Lancement local :   python app.py          -> http://localhost:8000
Production :        gunicorn app:app       (Render, Railway, Fly.io, VPS...)
"""
import os
from flask import Flask, send_from_directory, abort

BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=None)

FICHIERS_PUBLICS = {"index.html", "css", "js", "assets", "robots.txt"}


@app.route("/")
def accueil():
    return send_from_directory(BASE, "index.html")


@app.route("/<path:chemin>")
def statique(chemin):
    # On n'expose que les dossiers du site : jamais app.py ni requirements.txt
    if chemin.split("/")[0] not in FICHIERS_PUBLICS:
        abort(404)
    return send_from_directory(BASE, chemin)


@app.after_request
def entetes(rep):
    # Cache long pour les images, court pour le code
    if rep.mimetype and rep.mimetype.startswith("image/"):
        rep.headers["Cache-Control"] = "public, max-age=2592000"
    else:
        rep.headers["Cache-Control"] = "public, max-age=300"
    rep.headers["X-Content-Type-Options"] = "nosniff"
    rep.headers["X-Frame-Options"] = "DENY"
    rep.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return rep


@app.errorhandler(404)
def introuvable(_):
    # Site à page unique : toute route inconnue renvoie l'accueil
    return send_from_directory(BASE, "index.html"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
