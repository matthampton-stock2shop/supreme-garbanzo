from flask import Flask
import sqlite3
import os
import threading

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


_db = None
_lock = threading.RLock()

def init_db(dbname):
    global _db
    if _db is not None:
        raise ValueError("DB already initialised")
    _db = dbname

    with _lock:
        con = sqlite3.connect(_db)
        try:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS products(sku TEXT NOT NULL PRIMARY KEY, attributes TEXT)")
            con.commit()
        finally:
            con.close()




if __name__ == '__main__':
    init_db(os.path.join(os.path.dirname(__file__), "data", "db.sqlite"))
    app.run()