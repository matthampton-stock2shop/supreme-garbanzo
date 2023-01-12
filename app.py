from flask import Flask
import sqlite3
import os
import threading
import json

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

    db_execute(False, "CREATE TABLE IF NOT EXISTS products(sku TEXT NOT NULL PRIMARY KEY, attributes TEXT)")

def db_execute(is_query, sql, *args):
    rows = None
    with _lock:
        con = sqlite3.connect(_db, uri=True)
        try:
            cur = con.cursor()
            res = cur.execute(sql, *args)
            if is_query:
                rows = res.fetchall()
            con.commit()
        finally:
            con.close()
    return rows

def upsert_product(sku, attributes):
    attributes_j = json.dumps(attributes)
    db_execute(False,
        "INSERT INTO products(sku, attributes) VALUES(?, ?) ON CONFLICT(sku) DO UPDATE SET attributes=?",
        (sku, attributes_j, attributes_j))

def get_products():
    products = [
        {"sku": sku, "attributes": json.loads(attributes_j) if attributes_j else {}} 
        for sku, attributes_j in db_execute(True, "SELECT sku, attributes FROM products")
    ]
    return products



if __name__ == '__main__':
    init_db(os.path.join(os.path.dirname(__file__), "data", "db.sqlite"))
    app.run()