import sqlite3
import threading
import json
from contextlib import contextmanager

_db = None
_lock = threading.RLock()

def init(dbname):
    global _db
    if _db is not None:
        raise ValueError("DB already initialised")
    _db = dbname

    db_execute(False, "CREATE TABLE IF NOT EXISTS products(sku TEXT NOT NULL PRIMARY KEY, attributes TEXT)")

@contextmanager
def transaction():
    with _lock:
        con = sqlite3.connect(_db, uri=True)
        try:
            cur = con.cursor()
            yield cur
            con.commit()
        finally:
            con.close()

def db_execute(is_query, sql, *args):
    with transaction() as cur:
        res = cur.execute(sql, *args)
        if is_query:
            return res.fetchall()

def upsert_product(product):
    attributes_j = json.dumps(product.get('attributes') or {})
    db_execute(False,
        "INSERT INTO products(sku, attributes) VALUES(?, ?) ON CONFLICT(sku) DO UPDATE SET attributes=?",
        (product['sku'], attributes_j, attributes_j))

def get_products():
    products = [
        {"sku": sku, "attributes": json.loads(attributes_j) if attributes_j else {}} 
        for sku, attributes_j in db_execute(True, "SELECT sku, attributes FROM products")
    ]
    return products

def set_products(products):
    rows = [(product['sku'], json.dumps(product.get('attributes') or {})) for product in products]
    with transaction() as cur:
        cur.execute("DELETE FROM products")
        if rows:
            cur.executemany("INSERT INTO products(sku, attributes) VALUES(?, ?)", rows)
