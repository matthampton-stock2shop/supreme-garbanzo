import sqlite3
import threading
import json
from contextlib import contextmanager

_db = None
_lock = threading.RLock()

class ValidationError(Exception):
    pass

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

def validate_product(product):
    if not set(product.keys()).issubset({"sku", "attributes"}):
        raise ValidationError("Invalid properties")
    if not isinstance(product.get("sku"), str):
        raise ValidationError("Invalid or missing sku")
    if "attributes" in product and not isinstance(product.get("attributes"), dict):
        raise ValidationError("Invalid attributes")
    return product

def upsert_product(product):
    validate_product(product)
    attributes_j = json.dumps(product.get('attributes') or {})
    db_execute(False,
        "INSERT INTO products(sku, attributes) VALUES(?, ?) ON CONFLICT(sku) DO UPDATE SET attributes=?",
        (product['sku'], attributes_j, attributes_j))

def get_product(sku):
    row = db_execute(True, "SELECT attributes FROM products WHERE sku=?", (sku,))
    if row:
        return {"sku": sku, "attributes": json.loads(row[0][0]) if row[0][0] else {}} 

def get_products():
    products = [
        {"sku": sku, "attributes": json.loads(attributes_j) if attributes_j else {}} 
        for sku, attributes_j in db_execute(True, "SELECT sku, attributes FROM products")
    ]
    return products

def set_products(products):
    rows = [(product['sku'], json.dumps(validate_product(product).get('attributes') or {})) for product in products]
    with transaction() as cur:
        cur.execute("DELETE FROM products")
        if rows:
            cur.executemany("INSERT INTO products(sku, attributes) VALUES(?, ?)", rows)
