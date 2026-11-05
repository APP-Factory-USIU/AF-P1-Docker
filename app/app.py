import os

import redis
from flask import Flask, jsonify, redirect, render_template, url_for

app = Flask(__name__)
store = redis.Redis(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=6379,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


@app.get("/")
def index():
    return render_template("index.html", count=int(store.get("visits") or 0))


@app.post("/count")
def count():
    store.incr("visits")
    return redirect(url_for("index"), code=303)


@app.get("/health")
def health():
    store.ping()
    return jsonify(status="ok")


@app.errorhandler(redis.RedisError)
def redis_unavailable(error):
    app.logger.warning("Redis unavailable: %s", error)
    return "Redis is unavailable. Check the Redis host and service logs.\n", 503
