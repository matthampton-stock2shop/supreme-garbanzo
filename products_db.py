import sqlite3
import json
from contextlib import contextmanager

_db = None

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
        raise ValidationError("Invalid properties") # <-- throw new ValidationError("...")
    if not isinstance(product.get("sku"), str):
        raise ValidationError("Invalid or missing sku")
    if "attributes" in product and not isinstance(product.get("attributes"), dict):
        raise ValidationError("Invalid attributes")
    return product

def upsert_product(product):
    """
    {
       "sku": "ABC123",
       "attributes": {
           "foo": "bar",
           "size": "XL",
       }
    }
    """
    validate_product(product)
    attributes_j = json.dumps(product.get('attributes') or {}) # <-- JSON.stringify(product.attributes||{}) / json_encode(product["attributes"])
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
    rows = []
    for product in products:
        rows.append((product['sku'], json.dumps(validate_product(product).get('attributes') or {}))) # <-- JSON.stringify
    with transaction() as conn:
        conn.execute("DELETE FROM products")
        for row in rows:
            conn.execute("INSERT INTO products(sku, attributes) VALUES(?, ?)", row)

# Request: A, B, C
# Request: C, D, E


def upsert_product_alternative(product):
    """
    {
       "sku": "ABC123",
       "attributes": {
           "foo": "bar",
           "size": "XL",
       }
    }
    """
    validate_product(product)
    for (name, value) in product['attributes'].items():
        db_execute(False,
            "INSERT INTO product_attributes(sku, name, value) VALUES(?, ?, ?) ON CONFLICT(sku, name) DO UPDATE SET value=?",
            (product['sku'], name, value, value))
